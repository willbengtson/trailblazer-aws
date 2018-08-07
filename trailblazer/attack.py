import json
import re
import time

import boto3

from trailblazer import log
from trailblazer.boto.service import get_boto_functions, get_service_json_files, get_service_call_params, make_api_call
from trailblazer.boto.util import botocore_config


def make_call(config, session, service, command, region=None):
    # Grab a region to use for the calls.  This should be us-west-2
    if not region:
        region = session.get_available_regions(service)[-1]

    if config.get('user_agent', None):
        botocore_config.user_agent = config['user_agent']

    # Create a client with parameter validation off
    client = session.client(service, region_name=region, config=botocore_config)

    # Get the functions that you can call
    functions_list = get_boto_functions(client)

    # Get the service file
    service_file_json = get_service_json_files(config)

    # Get a list of params needed to make the serialization pass in botocore
    service_call_params = get_service_call_params(service_file_json[service])


    for function in functions_list:
        if function[0] == command:

            # The service_file_json doesn't have underscores in names so let's remove them
            function_key = function[0].replace('_','')

            # We need to pull out the parameters needed in the requestUri, ex. /{Bucket}/{Key+} -> ['Bucket', 'Key']
            params = re.findall('\{(.*?)\}', service_call_params.get(function_key, '/'))
            params = [p.strip('+') for p in params]

            func_params = {}

            for param in params:
                func_params[param] = 'testparameter'

            try:
                make_api_call(service, function, region, func_params)
            except ClientError as e:
                log.debug(e)
            except boto3.exceptions.S3UploadFailedError as e:
                log.debug(e)
            except TypeError as e:
                log.debug(e)
            except KeyError as e:
                log.debug('Unknown Exception: {}.{} - {}'.format(service, function[0], e))

            return


def simulate_attack(config, commands, dry_run=False):
    log.debug('Attack chain to be executed:')
    log.debug(json.dumps(commands, indent=4))

    session = boto3.Session()

    for command in commands:
        service_event = command['call'].split('.')

        service = service_event[0]
        api_call = service_event[1]

        delay = command.get('time_delay', 0)
        region = command.get('region', None)

        log.info('Making call - {}.{}'.format(service, api_call))
        if not dry_run:
            make_call(config, session, service, api_call, region)
        log.info('Sleeping {} until next call'.format(delay))
        if not dry_run:
            time.sleep(delay)

