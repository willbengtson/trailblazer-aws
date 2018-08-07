from inspect import getmembers, isfunction, ismethod
import json
import os
import re
import time

import boto3
import botocore
from botocore.exceptions import ClientError

from trailblazer import log
from trailblazer.boto.util import botocore_config


def get_service_json_files(config):
    service_file = {}

    root_dir = config['botocore_document_json_path']

    for service_dir in os.listdir(root_dir):
        if os.path.isdir(os.path.join(root_dir,service_dir)):
            date_dirs = os.listdir(os.path.join(root_dir,service_dir))
            date_dir = None
            if len(date_dirs) > 1:
                date_dir = date_dirs[-1]
            else:
                date_dir = date_dirs[0]
            if os.path.exists(os.path.join(root_dir, service_dir, date_dir, 'service-2.json')):
                service_file[service_dir] = os.path.join(root_dir, service_dir, date_dir, 'service-2.json')
            else:
                service_file[service_dir] = None

    return service_file

def get_service_call_params(service_json_file):

    services = {}

    json_data = json.load(open(service_json_file))

    for key, value in json_data.get('operations', {}).items():
        services[key.lower()] = value.get('http', {}).get('requestUri', '/')

    return services


def get_service_call_mutation(service_json_file):

    services = {}

    json_data = json.load(open(service_json_file))

    for key, value in json_data.get('operations', {}).items():

        method = value.get('http', {}).get('method', 'UNKOWN')

        if method == 'GET':
            services[key.lower()] = 'nonmutating'
        else:
            services[key.lower()] = 'mutating'

    return services


def get_boto_functions(client):
    """Loop through the client member functions and pull out what we can actually call"""
    functions_list = [o for o in getmembers(client) if ( ( isfunction(o[1]) or ismethod(o[1]) )
            and not o[0].startswith('_') and not o[0] == 'can_paginate' and not o[0] == 'get_paginator'
            and not o[0] == 'get_waiter' and 'presigned' not in o[0])]

    return functions_list


def make_api_call(service, function, region, func_params):

    if function[0] == 'generate_presigned_url':
        func_params['ClientMethod'] = 'get_object'

    if service == 's3':
        if function[0] == 'copy':
            copy_source = {
                'Bucket': 'mybucket',
                'Key': 'mykey'
            }
            function[1](copy_source, 'testbucket', 'testkey')
            time.sleep(.1)
            return
        elif function[0] == 'download_file':
            function[1]('testbucket', 'testkey', 'test')
            time.sleep(.1)
            return
        elif function[0] == 'download_fileobj':
            with open('testfile', 'wb') as data:
                function[1]('testbucket', 'testkey', data)
                time.sleep(.1)
                return
        elif function[0] == 'upload_file':
            function[1](service_file_json[service], 'testbucket', 'testkey')
            time.sleep(.1)
            return
        elif function[0] == 'upload_fileobj':
            with open(service_file_json[service], 'rb') as data:
                function[1](data, 'testbucket', 'testkey')
                time.sleep(.1)
                return
    elif service == 'ec2':
        if function[0] == 'copy_snapshot':
            function[1](SourceRegion=region, **func_params)
            time.sleep(.1)

    function[1](**func_params)
    time.sleep(.1)
    return
