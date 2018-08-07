import logging
import json
from inspect import getmembers, isfunction, ismethod
import os
import sys
import yaml

import boto3
import click
import click_log
from click.exceptions import UsageError

from trailblazer import log
from trailblazer.__about__ import __version__
from trailblazer.boto.service import get_service_json_files, get_service_call_params
from trailblazer.attack import simulate_attack
from trailblazer.cloudtrail import process_cloudtrail, record_cloudtrail
from trailblazer.enumerate import enumerate_services


click_log.basic_config(log)


class YAML(click.ParamType):
    name = 'yaml'

    def convert(self, value, param, ctx):
        try:
            with open(value, 'rb') as f:
                return yaml.safe_load(f.read())
        except (IOError, OSError) as e:
            self.fail('Could not open file: {0}'.format(value))


class CommaList(click.ParamType):
    name = 'commalist'

    def convert(self, value, param, ctx):
        return value.split(',')


class AppContext(object):
    def __init__(self):
        self.config = None
        self.dry_run = False


pass_context = click.make_pass_decorator(AppContext, ensure=True)


@click.group()
@click_log.simple_verbosity_option(log)
@click.option('--config', type=YAML(), help='Configuration file to use.')
@click.option('--dry-run', type=bool, default=False, is_flag=True, help='Run command without persisting anything.')
@click.version_option(version=__version__)
@pass_context
def cli(ctx, config, dry_run):

    if not ctx.config:
        ctx.config = config

    if not ctx.dry_run:
        ctx.dry_run = dry_run

        log.debug('Current context. DryRun: {} Config: {}'.format(ctx.dry_run, json.dumps(ctx.config, indent=2)))

    if not ctx.config.get('botocore_document_json_path', None):
        log.fatal('botocore_document_json_path not defined in config file')


@cli.group()
def enumerate():
    pass


@cli.group()
def simulate():
    pass


@cli.group()
def cloudtrail():
    pass


@enumerate.command()
@click.option('--services', type=CommaList(), help='Comma delimited list of services')
@pass_context
def cloudtrail_calls(ctx, services):
    """Enumerate all calls for AWS Services to determine what shows up in CloudTrail"""
    log.info('Starting enumeration for CloudTrail...')

    session = boto3.Session()

    if not services:
        services = session.get_available_services()

    enumerate_services(ctx.config, services, dry_run=ctx.dry_run)

    log.info('Enumeration complete')


@simulate.command()
@pass_context
def attack(ctx):
    """Simulate an attack by making the calls described in the config"""
    if not ctx.config.get('attack_chain', None):
        log.fatal('attack_chain not found in config file')

    log.info('Starting attack simulation...')

    attack_commands = ctx.config['attack_chain']

    simulate_attack(ctx.config, attack_commands, dry_run=ctx.dry_run)

    log.info('Attack simulation complete')


@cloudtrail.command()
@click.option('--directory', type=str, help='Path to directory with CloudTrail files', required=True)
@click.option('--arn', type=str, help='User ARN making calls', required=True)
@pass_context
def process(ctx, directory, arn):
    """Process cloudtrail files"""
    log.info('Processing CloudTrail...')

    if not os.path.exists(directory):
        log.fatal('Invalid Directory Path')

    files = []
    for cloudtrail_file in os.listdir(directory):
        files.append(os.path.join(directory, cloudtrail_file))

    api_calls_logged = process_cloudtrail(arn, files)


@cloudtrail.command()
@click.option('--directory', type=str, help='Path to directory with CloudTrail files', required=True)
@click.option('--arn', type=str, help='User ARN making calls', required=True)
@click.option('--output', type=str, help='Output File Name')
@pass_context
def record(ctx, directory, arn, output):
    """Create attack simulation from CloudTrail"""
    log.info('Recording CloudTrail...')

    if not os.path.exists(directory):
        log.fatal('Invalid Directory Path')

    files = []
    for cloudtrail_file in os.listdir(directory):
        files.append(os.path.join(directory, cloudtrail_file))

    api_calls_recorded = record_cloudtrail(arn, files)

    if output:
        with open(output, 'w') as yaml_file:
            yaml.dump(
                {
                    'attack_chain': api_calls_recorded
                },
                yaml_file,
                default_flow_style=False
            )

if __name__ == '__main__':
    try:
        cli()
    except KeyboardInterrupt:
        logging.debug("Exiting due to KeyboardInterrupt...")

