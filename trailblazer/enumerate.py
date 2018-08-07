import re

import boto3
from botocore.exceptions import ClientError

from trailblazer import log
from trailblazer.boto.util import botocore_config
from trailblazer.boto.service import get_boto_functions, get_service_call_params, \
									get_service_json_files, make_api_call, get_service_call_mutation
from trailblazer.boto.sts import get_assume_role_session


def enumerate_services(config, services, dry_run=False):

    # Create a boto3 session to use for enumeration
    session = boto3.Session()

    authorized_calls = []

    for service in services:

        if len(session.get_available_regions(service)) == 0:
            log.debug('Skipping {} - No regions exist for this service'.format(service))
            continue

        # Create a service client
        log.info('Creating {} client...'.format(service))

        # Grab a region to use for the calls.  This should be us-west-2
        region = session.get_available_regions(service)[-1]

        # Set the user-agent if specified in the config
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

        # Loop through all the functions and call them
        for function in functions_list:

            # The service_file_json doesn't have underscores in names so let's remove them
            function_key = function[0].replace('_','')

            # Session Name Can only be 64 characters long
            if len(function_key) > 64:
                session_name = function_key[:63]
                log.info('Session Name {} is for {}'.format(session_name, function_key))
            else:
                session_name = function_key

            # Set the session to the name of the API call we are making
            session = get_assume_role_session(
                account_number=config['account_number'],
                role=config['account_role'],
                session_id=session_name
            )

            new_client = session.client(service, region_name=region, config=botocore_config)
            new_functions_list = get_boto_functions(new_client)

            for new_func in new_functions_list:
                if new_func[0] == function[0]:

                    # We need to pull out the parameters needed in the requestUri, ex. /{Bucket}/{Key+} -> ['Bucket', 'Key']
                    params = re.findall('\{(.*?)\}', service_call_params.get(function_key, '/'))
                    params = [p.strip('+') for p in params]

                    try:
                        func_params = {}

                        for param in params:
                            # Set something because we have to
                            func_params[param] = 'testparameter'

                        log.info('Calling {}.{} with params {} in {}'.format(service, new_func[0], func_params, region))

                        if not dry_run:
                        	make_api_call(service, new_func, region, func_params)

                    except ClientError as e:
                        log.debug(e)
                    except boto3.exceptions.S3UploadFailedError as e:
                        log.debug(e)
                    except TypeError as e:
                        log.debug(e)
                    except KeyError as e:
                        log.debug('Unknown Exception: {}.{} - {}'.format(service, new_func[0], e))
