# AWS TrailBlazer

TrailBlazer is a tool written to determine what AWS API calls are logged by CloudTrail and what they are logged as.  You can also use TrailBlazer as an attack simulation framework.

## How does it work?

TrailBlazer uses the python AWS SDK library called `boto3` in order to make the API calls into AWS.  It enumerates the services provided in the SDK, regions the services are available, and then determines what API calls there are for the given service by exploring the function set.  In order to enumerate the entire AWS SDK, TrailBlazer bypasses the `boto3` client-side validation to make mostly improper requests into AWS.  Mostly is the keyword here due to the fact that if an API call does not require a parameter, the API call sent by TrailBlazer will be 100% valid.  Due to the way AWS logs, these requests will be logged as `Invalid Parameters` or `Unauthorized` due to the inconsistency in CloudTrail logging.

## Getting Started

Install TrailBlazer:

`pip install trailblazer-aws`

### Setup AWS Permissions

Create an AWS Role called `trailblazer`

Create an inline policy with the following JSON object
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "sts:AssumeRole",
            "Resource": "arn:aws:iam::<account_number>:role/trailblazer"
        },
        {
            "Effect": "Deny",
            "Action": "*",
            "Resource": "*"
        }
    ]
}
```

Setup a trust relationship so that you it `AssumeRole` to itself:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::<account_number>:role/trailblazer"
      },
      "Action": "sts:AssumeRole",
      "Condition": {}
    }
  ]
}
```

### Clone the AWS Botocore Github project

TrailBlazer uses the JSON files found under the `botocore` project `data` directory to determine if a parameter is necessary for the `API` call.

```cd /tmp
git clone git@github.com:boto/botocore.git
```

## Command Line Options

You can determine what options are available by issuing the following command:

```
trailblazer --help
Usage: trailblazer [OPTIONS] COMMAND [ARGS]...

Options:
  -v, --verbosity LVL  Either CRITICAL, ERROR, WARNING, INFO or DEBUG
  --config YAML        Configuration file to use.
  --dry-run            Run command without persisting anything.
  --version            Show the version and exit.
  --help               Show this message and exit.

Commands:
  cloudtrail
  enumerate
  simulate
```

## Enumerate API calls for a given service

The following example will enumerate all calls for the `EC2` service:

`trailblazer --verbosity INFO --config <path_to_config> enumerate cloudtrail_calls --services ec2`

You will see output similar to the following:

```trailblazer --verbosity INFO --config config/test-config.yaml enumerate cloudtrail_calls --services ec2
Starting enumeration for CloudTrail...
Creating ec2 client...
Calling ec2.accept_reserved_instances_exchange_quote with params {} in us-west-2
Calling ec2.accept_vpc_endpoint_connections with params {} in us-west-2
Calling ec2.accept_vpc_peering_connection with params {} in us-west-2
Calling ec2.allocate_address with params {} in us-west-2
Calling ec2.allocate_hosts with params {} in us-west-2
Calling ec2.assign_ipv6_addresses with params {} in us-west-2
Calling ec2.assign_private_ip_addresses with params {} in us-west-2
Calling ec2.associate_address with params {} in us-west-2
Calling ec2.associate_dhcp_options with params {} in us-west-2
Calling ec2.associate_iam_instance_profile with params {} in us-west-2
Calling ec2.associate_route_table with params {} in us-west-2
Calling ec2.associate_subnet_cidr_block with params {} in us-west-2
Calling ec2.associate_vpc_cidr_block with params {} in us-west-2
Calling ec2.attach_classic_link_vpc with params {} in us-west-2
Calling ec2.attach_internet_gateway with params {} in us-west-2
Calling ec2.attach_network_interface with params {} in us-west-2
Calling ec2.attach_volume with params {} in us-west-2
Calling ec2.attach_vpn_gateway with params {} in us-west-2
Calling ec2.authorize_security_group_egress with params {} in us-west-2
Calling ec2.authorize_security_group_ingress with params {} in us-west-2
Calling ec2.bundle_instance with params {} in us-west-2
Calling ec2.cancel_bundle_task with params {} in us-west-2
Calling ec2.cancel_conversion_task with params {} in us-west-2
Calling ec2.cancel_export_task with params {} in us-west-2
Calling ec2.cancel_import_task with params {} in us-west-2
Calling ec2.cancel_reserved_instances_listing with params {} in us-west-2
Calling ec2.cancel_spot_fleet_requests with params {} in us-west-2
Calling ec2.cancel_spot_instance_requests with params {} in us-west-2
...
```

## Determine what was logged in CloudTrail

`trailblazer --verbosity INFO --config config/test-config.yaml cloudtrail process --directory /tmp/cloudtrail --arn arn:aws:sts::123456789123:assumed-role/trailblazer`

You should see an output similar to below:

```Processing CloudTrail...
EventSource, EventName, Recorded Name, Match
ec2, AuthorizeSecurityGroupEgress, authorizesecuritygroupegress, True
ec2, AssociateIamInstanceProfile, associateiaminstanceprofile, True
ec2, AssignIpv6Addresses, assignipv6addresses, True
ec2, AcceptVpcPeeringConnection, acceptvpcpeeringconnection, True
ec2, CreateFpgaImage, createfpgaimage, True
ec2, AttachClassicLinkVpc, attachclassiclinkvpc, True
ec2, AssociateDhcpOptions, associatedhcpoptions, True
ec2, CancelExportTask, cancelexporttask, True
ec2, CreateEgressOnlyInternetGateway, createegressonlyinternetgateway, True
ec2, CancelBundleTask, cancelbundletask, True
ec2, CancelSpotInstanceRequests, cancelspotinstancerequests, True
ec2, AttachNetworkInterface, attachnetworkinterface, True
ec2, CreateCustomerGateway, createcustomergateway, True
ec2, CreateDefaultSubnet, createdefaultsubnet, True
ec2, CancelReservedInstancesListing, cancelreservedinstanceslisting, True
ec2, CopySnapshot, copysnapshot, True
ec2, AttachVolume, attachvolume, True
ec2, CancelSpotFleetRequests, cancelspotfleetrequests, True
ec2, BundleInstance, bundleinstance, True
ec2, CopyFpgaImage, copyfpgaimage, True
ec2, AcceptReservedInstancesExchangeQuote, acceptreservedinstancesexchangequote, True
ec2, CancelConversionTask, cancelconversiontask, True
ec2, AssociateAddress, associateaddress, True
ec2, CreateDhcpOptions, createdhcpoptions, True
ec2, AssociateRouteTable, associateroutetable, True
ec2, AssociateSubnetCidrBlock, associatesubnetcidrblock, True
ec2, AuthorizeSecurityGroupIngress, authorizesecuritygroupingress, True
ec2, AcceptVpcEndpointConnections, acceptvpcendpointconnections, True
ec2, ConfirmProductInstance, confirmproductinstance, True
ec2, AllocateAddress, allocateaddress, True
ec2, AttachInternetGateway, attachinternetgateway, True
ec2, AllocateHosts, allocatehosts, True
ec2, AssociateVpcCidrBlock, associatevpccidrblock, True
ec2, AttachVpnGateway, attachvpngateway, True
ec2, CreateDefaultVpc, createdefaultvpc, True
ec2, AssignPrivateIpAddresses, assignprivateipaddresses, True
ec2, CopyImage, copyimage, True
...
```


# Using TrailBlazer for Attack Simulation

TrailBlazer can be used to model attacks in your environment to aid in testing monitoring.  Due to the way that TrailBlazer makes calls, you can safely use TrailBlazer in your production environment to model an attacker in your environment.

You can use the attack simulation mode in two ways:

* CLI
* Library

To use the CLI, issue the following command:

`trailblazer --verbosity INFO --config <path_to_config> simulate attack`

The `config.yaml` file provided under `config/` shows an example attach chain:

```yaml
attack_chain:
  - call: sts.get_caller_identity
    time_delay: 2
  - call: cloudtrail.describe_trails
    time_delay: 1
  - call: s3.list_buckets
    time_delay: 3
  - call: ec2.describe_instances
    time_delay: 3
```

This attack chain would call `sts.get_caller_identity`, wait 2 seconds, call `cloudtrail.describe_trails`, wait 1 second, and conitnue making the calls until finished.  The `call` is defined by the `boto3` function names.  More on `boto3` can be found [here](https://boto3.readthedocs.io/en/latest/).

When you want to run tests in your environment to make sure you are able to detect certain API calls or chains of API calls, you can use TrailBlazer into your own automation framework.

To use TrailBlazer as a library, you can do something like:

```python
from trailblazer.attack import simulate_attack

config = {
    'botocore_document_json_path': '/tmp/botocore/botocore/data'
}

commands = [
    {
        'call': 'sts.get_caller_identity',
        'time_delay': 1
    },
    {
        'call': 'cloudtrail.describe_trails',
        'time_delay': 1
    }
]

simulate_attack(config, commands)
```

You should see these calls then show up in your CloudTrail

![Attack Simulate CloudTrail](/images/attack_simulation_ct.png "Attack Simulate CloudTrail")


