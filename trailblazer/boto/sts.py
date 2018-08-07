import boto3
from botocore.exceptions import ClientError

from trailblazer import log


def get_assume_role_session(account_number, role, session_id):
    arn = "arn:aws:iam::{}:role/{}".format(account_number, role)

    try:
    	session = boto3.Session()
    	sts = session.client('sts')
    	assumed_role = sts.assume_role(RoleArn=arn, RoleSessionName=session_id)
    except ClientError as e:
    	log.fatal(e)
    else:
    	session = boto3.Session(
    		aws_access_key_id=assumed_role['Credentials']['AccessKeyId'],
    		aws_secret_access_key=assumed_role['Credentials']['SecretAccessKey'],
    		aws_session_token=assumed_role['Credentials']['SessionToken']
    	)
    	return session
