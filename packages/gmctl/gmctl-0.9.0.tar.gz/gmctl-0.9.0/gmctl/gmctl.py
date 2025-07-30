# -----------------------------------------------------------------------------
# Copyright (c) 2025 SKAI Software Corporation. All rights reserved.
#
# This software and associated documentation files (the "Software") are the
# exclusive property of SKAI Software Corporation. Unauthorized copying,
# modification, distribution, resale, or use of this software or its components,
# in whole or in part, is strictly prohibited.
#
# The Software is licensed, not sold. All rights, title, and interest in and to
# the Software, including all associated intellectual property rights, remain
# with SKAI Software Corporation.
# -----------------------------------------------------------------------------

from dotenv import load_dotenv
load_dotenv() 

import logging
logging.basicConfig(level=logging.ERROR, format='gmctl - %(name)s - %(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

import click
import urllib.parse
from gmctl.riskiq import riskiq
from gmctl.repository import repo
from gmctl.commit import commit
from gmctl.ecs_deployment import ecs
from gmctl.lambda_deployment import lambda_cmd
from gmctl.k8s_deployment import k8s
from gmctl.utils import print_table
from gmctl.db_functions import get_deployments
from gmctl.gmclient import GitmoxiClient
import os

@click.group()
@click.option('-e', '--endpoint-url', default="env(GITMOXI_ENDPOINT_URL), fallback to http://127.0.0.1:8080", help='The Gitmoxi FastAPI endpoint URL', show_default=True)
@click.option('-l', '--log-level', default="ERROR", type=click.Choice(["DEBUG","INFO","WARNING","ERROR","CRITICAL"], case_sensitive=False), help='The log level', show_default=True)
@click.pass_context
def cli(ctx, endpoint_url ,log_level):
    logging.getLogger().setLevel(getattr(logging, log_level.upper()))
    ctx.ensure_object(dict)
    endpoint_url = ctx.obj.get('ENDPOINT_URL', None)
    if not endpoint_url:
        endpoint_url = os.getenv('GITMOXI_ENDPOINT_URL', 'http://127.0.0.1:8080')
    ctx.obj['ENDPOINT_URL'] = endpoint_url

cli.add_command(commit)
cli.add_command(repo)
cli.add_command(riskiq)


# Deployment group with subcommands
@cli.group()
@click.pass_context
def deployment(ctx):
    """User related commands."""
    pass

deployment.add_command(ecs)
deployment.add_command(lambda_cmd)
deployment.add_command(k8s)

@deployment.command()
@click.option('-c', '--commit-hash', help='The commit hash', required=True)
@click.option('-N', '--number-of-records', help='Number of records', default=10)
@click.pass_context
def get(ctx, commit_hash, number_of_records):
    """
    Retrieve ECS and Lambda deployment records for a specific commit.

    Args:
        commit_hash (str): The commit hash to filter deployments.

    Example:
        gmctl deployment get -c abc123

    This command retrieves deployment records for both ECS and Lambda services
    associated with the specified commit hash. It displays the deployment details
    in a tabular format for each service.
    """
    try:
        gmclient = GitmoxiClient(ctx.obj['ENDPOINT_URL'])
        keys = {}
        keys["ecs"] = ["repo_url", "commit_hash", "account_id", "region", "service", 
                        "cluster", "create_timestamp", "status", "file_prefix"]
        keys["lambda"] = ["repo_url", "commit_hash", "account_id", "region", 
                          "function_name", "create_timestamp", "status", "file_prefix"]
        for service in ["ecs", "lambda"]:
            click.echo(f"{service.upper()} deployments for commit {commit_hash}:")
            conditions = { "commit_hash": commit_hash}
            deployments = get_deployments(service, gmclient, conditions, number_of_records)
            to_display = []
            for deployment in deployments:
                to_display.append({k: deployment.get(k) for k in keys[service]})
            print_table(to_display)
    except Exception as e:
        click.echo(f"Error: {e}")


# Rebalance group with subcommands
@cli.group()
@click.pass_context
def taskset(ctx):
    """User related commands."""
    pass

@taskset.command()
@click.option('-s', '--service_arn', help='ECS service ARN', required=True)
@click.option('-r', '--revert', is_flag=True, help='Revert capacity from fallback to primary')
@click.option('-A', '--shift_all', is_flag=True, help='Shift all capacity. Otherwise only adjust the required amount')
@click.option('-o', '--override', is_flag=True, help='Redo even if the record is PROCESSING state')
@click.pass_context
def rebalance(ctx, service_arn, revert, shift_all, override):
    try:
        resource_path = f"/taskset/rebalance"
        payload = {"service_arn":service_arn, "shift_all":shift_all, "revert":revert, "override":override}
        # make a POST call to the /commits/deploy endpoint
        gmclient = GitmoxiClient(ctx.obj['ENDPOINT_URL'])
        scale_response = gmclient.post(resource_path, payload)
        to_display = []
        if scale_response:
            tasksets = scale_response.get("tasksets", [])
            for ts in tasksets:
                from_taskset_arn = ts.get("taskset_arn") if not revert else ts.get("fallback_taskset_arn")
                to_taskset_arn = ts.get("fallback_taskset_arn") if not revert else ts.get("taskset_arn")
                amount = "ALL" if shift_all else "AS_NEEDED"
                to_display.append({"from_taskset_arn": from_taskset_arn, "to_taskset_arn": to_taskset_arn, "amount": amount})
        print_table(to_display)

    except Exception as e:
        click.echo(f"Error: {e}")

@taskset.command()
@click.option('-t', '--taskset_arn', help='ECS Taskset ARN', required=True)
@click.pass_context
def get(ctx, taskset_arn):
    try:
        encoded_arn = urllib.parse.quote(taskset_arn, safe='')
        resource_path = f"/taskset?taskset_arn={encoded_arn}"
        gmclient = GitmoxiClient(ctx.obj['ENDPOINT_URL'])
        scale_response = gmclient.get(resource_path)
        if scale_response:
            scale_tasksets = scale_response.get("tasksets", [])
            keys = ["taskset_arn", "fallback_taskset_arn", "primary_scale", "fallback_scale"]
            to_display = []
            for ts in scale_tasksets:
                to_display.append({k: ts.get(k) for k in keys})
            print_table(to_display)
        else:
            click.echo(f"Error: No records found for {taskset_arn}")
    except Exception as e:
        click.echo(f"Error: {e}")

