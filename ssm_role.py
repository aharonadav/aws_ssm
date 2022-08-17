#!/usr/bin/python3
import boto3
from botocore.exceptions import ClientError
import logging
import time

# Set up logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

class EC2:
    def __init__(self,account_id,roleName,region):
        self.account_id = account_id
        self.roleName   = roleName
        self.region     = region

    def __IAM__(self):
        cw_trust_policy = '''{
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "ec2.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }'''

        client = boto3.client('iam')
        logger.info('Create IAM Role for ClowdWatch and SSM:\n')
        try:
            response = client.create_role(
                Path='/',
                RoleName=self.roleName,
                AssumeRolePolicyDocument=cw_trust_policy,
                Description='SSM and ClowdWatch permissions for EC2'
            )
            logger.info(response)
        except ClientError as error:
            logger.debug(error)

        logger.info('Creating instance profile for EC2')
        try:
            client = boto3.client('iam')
            response = client.create_instance_profile(
                InstanceProfileName=self.roleName,
                Path='/'
            )
            print('Instance profile created.\n',response)
        except ClientError as error:
            logger.info(error)

        logger.info('Attaching instance profile for IAM role')
        try:
            response = client.add_role_to_instance_profile (
                InstanceProfileName = self.roleName,
                RoleName            = self.roleName
            )
            logger.info(response)
            logger.info('Instance profile attached to role %s successfully.\n' % self.roleName,response)
            EC2.IAMPoliciesChecker(self,self.roleName)

        except ClientError as error:
            if error.response['Error']['Code'] == 'LimitExceeded':
                print('Role already attached to instance profile')
            else:
                logger.info(error)

    def AddIAMRole(self,instance_id):
        client = boto3.client('ec2',region_name=self.region)
        try:
            response = client.associate_iam_instance_profile(
                IamInstanceProfile={
                    'Arn': f'arn:aws:iam::{self.account_id}:instance-profile/{self.roleName}',
                    'Name': self.roleName
                },
                InstanceId=instance_id
            )
            return response
        except ClientError as error:
            logger.info(error)

    def IAMPoliciesChecker(self,role):
        logger.debug(f'Function: {EC2.IAMPoliciesChecker.__name__}')
        role_policies = [
                    'arn:aws:iam::aws:policy/service-role/AmazonEC2RoleforSSM',
                    'arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore'
        ]
        client = boto3.client('iam')
        try:
            response = client.get_instance_profile(
                InstanceProfileName=role
            )
            logger.info(response)
            roleName = response['InstanceProfile']['Roles'][0]['RoleName']
            logger.info(f'Role name for attaching policy: {roleName}')
        except ClientError as error:
            logger.info(error)
        
        
        try:
            for policy in role_policies:
                response = client.attach_role_policy(
                    RoleName=roleName,
                    PolicyArn=policy
                )
                logger.info(response)
        except ClientError as error:
            logger.info(error)

    def describeInstances(self):
        logger.info('Scanning instances')
        instances_list = []
        try:
            client = boto3.client('ec2',region_name=self.region)
            response = client.describe_instances(
                Filters=[
                    {
                        'Name': 'tag:ssm',
                        'Values': [
                            'true',
                        ]
                    },
                ],
            )
            response = response['Reservations']
            for i in response:
                instance = (i['Instances'])
                logger.debug(f'\nFull response: {instance}')
                id   = instance[0]['InstanceId']
                logger.info(f'Instance ID: {id}\n')
                try:
                    role = instance[0]['IamInstanceProfile']
                    if (self.roleName in role):
                        logger.info(f'SSM RoleName {self.roleName} already attached to instance ID {id}')
                        continue
                    else:
                        name = role['Arn'].split('/')[1]
                        x = EC2.IAMPoliciesChecker(self,name)
                        print(x)
                        print('Adding policies')        
                    logger.info(id)
                    instances_list.append(id)
                except:
                    EC2.AddIAMRole(self,id)
        except ClientError as error:
            logger.debug(error)
        
        return instances_list

cw = EC2(
    '553686865554',
    'SSM_ClowdWatch_Rolenewest1',
    'eu-west-1'
    )
cw.__IAM__() #Create IAM role for CW and SSM
cw.describeInstances()
#cw.IAMPoliciesChecker('SSM_ClowdWatch_RoleNEW1')


