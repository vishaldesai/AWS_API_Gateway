from __future__ import print_function
import boto3
import botocore
import time
import sys
import argparse
import json
import os

'''AWS Organizations Create Account and Provision Resources via CloudFormation

This module creates a new account using Organizations, then calls CloudFormation to deploy baseline resources within that account via a local tempalte file.

'''

__version__ = '0.1'
__author__ = '@author@'
__email__ = '@email@'


def create_account(
        account_name,
        account_email,
        account_role,
        access_to_billing,
        organization_unit_id,
        scp):
    '''
        Create a new AWS account and add it to an organization
    '''

    client = boto3.client('organizations')
    try:
        create_account_response = client.create_account(Email=account_email, AccountName=account_name,
                                                        RoleName=account_role,
                                                        IamUserAccessToBilling=access_to_billing)
    except botocore.exceptions.ClientError as e:
        print(e)
        sys.exit(1)

    time.sleep(10)

    account_status = 'IN_PROGRESS'
    while account_status == 'IN_PROGRESS':
        create_account_status_response = client.describe_create_account_status(
            CreateAccountRequestId=create_account_response.get('CreateAccountStatus').get('Id'))
        print("Create account status " + str(create_account_status_response))
        account_status = create_account_status_response.get(
            'CreateAccountStatus').get('State')
    if account_status == 'SUCCEEDED':
        account_id = create_account_status_response.get(
            'CreateAccountStatus').get('AccountId')
    elif account_status == 'FAILED':
        print("Account creation failed: " +
              create_account_status_response.get('CreateAccountStatus').get('FailureReason'))
        sys.exit(1)
    root_id = client.list_roots().get('Roots')[0].get('Id')

    # Move account to the org
    if organization_unit_id is not None:
        try:
            describe_organization_response = client.describe_organizational_unit(
                OrganizationalUnitId=organization_unit_id)
            move_account_response = client.move_account(AccountId=account_id, SourceParentId=root_id,
                                                        DestinationParentId=organization_unit_id)
        except Exception as ex:
            template = "An exception of type {0} occurred. Arguments:\n{1!r} "
            message = template.format(type(ex).__name__, ex.args)
            # create_organizational_unit(organization_unit_id)
            print(message)

    # Attach policy to account if exists
    if scp is not None:

        attach_policy_response = client.attach_policy(
            PolicyId=scp, TargetId=account_id)
        print("Attach policy response " + str(attach_policy_response))

    return account_id


def assume_role(account_id, account_role):
    '''
        Assume admin role within the newly created account and return credentials
    '''

    sts_client = boto3.client('sts')
    role_arn = 'arn:aws:iam::' + account_id + ':role/' + account_role

    # Call the assume_role method of the STSConnection object and pass the role
    # ARN and a role session name.

    assuming_role = True
    while assuming_role is True:
        try:
            assuming_role = False
            assumedRoleObject = sts_client.assume_role(
                RoleArn=role_arn,
                RoleSessionName="NewAccountRole"
            )
        except botocore.exceptions.ClientError as e:
            assuming_role = True
            print(e)
            print("Retrying...")
            time.sleep(10)

    # From the response that contains the assumed role, get the temporary
    # credentials that can be used to make subsequent API calls
    return assumedRoleObject['Credentials']


def get_template(template_file):

    print("Reading resources from " + template_file)
    head, tail = os.path.split(template_file)
    template_file1 = tail
    s3 = boto3.resource('s3')
    obj = s3.Object('vishaldxc', template_file1)
    cf_template = obj.get()['Body'].read().decode('utf-8')
    return cf_template


def deploy_resources(credentials, template, stack_name, stack_region):
    '''
        Create a CloudFormation stack of resources within the new account
    '''

    datestamp = time.strftime("%d/%m/%Y")
    client = boto3.client('cloudformation',
                          aws_access_key_id=credentials['AccessKeyId'],
                          aws_secret_access_key=credentials['SecretAccessKey'],
                          aws_session_token=credentials['SessionToken'],
                          region_name=stack_region)

    print("Creating stack " + stack_name + " in " + stack_region)

    creating_stack = True
    counter = 0
    while creating_stack is True:
        try:
            creating_stack = False
            if counter > 3:
                return
            counter = counter + 1
            create_stack_response = client.create_stack(
                StackName=stack_name,
                TemplateBody=template,
                Capabilities=[
                    'CAPABILITY_NAMED_IAM',
                ]
            )
        except botocore.exceptions.ClientError as e:
            creating_stack = True
            print(e)
            print("Retrying...")
            time.sleep(10)

    stack_building = True
    print("Stack creation in process...")
    ''' Below code is required for synchronous behaviour
    #print(create_stack_response)
    while stack_building is True:
        event_list = client.describe_stack_events(
            StackName=stack_name).get("StackEvents")
        stack_event = event_list[0]

        if (stack_event.get('ResourceType') == 'AWS::CloudFormation::Stack' and
                stack_event.get('ResourceStatus') == 'CREATE_COMPLETE'):
            stack_building = False
            print("Stack construction complete.")
        elif (stack_event.get('ResourceType') == 'AWS::CloudFormation::Stack' and
              stack_event.get('ResourceStatus') == 'ROLLBACK_COMPLETE'):
            stack_building = False
            print(stack_event)
            print("Stack construction failed.")
            sys.exit(1)
        else:
            print(stack_event)
            print("Stack building . . .")
            time.sleep(10)

    stack = client.describe_stacks(StackName=stack_name)
    return stack
    '''

    return 1


def get_account_list():
  """
  Get list of accounts
  return: List of account Ids
  """
  account_list = {}
  # Get a list of accounts in our org
  client = boto3.client('organizations')
  response = client.list_accounts()
  # We expect there to be at least 10 accounts and form json in account: Name format
  for account in response['Accounts']:
    account_list[account['Id']] = account['Name']

  while 'NextToken' in response:
    print("NextToken")
    for account in response['Accounts']:
      account_list.update(account['Name'])

    response = client.list_accounts(
        MaxResults=10,
        NextToken=response['NextToken']
    )
  return account_list


def lambda_handler(event, context):
    #def main(arguments):
    print(event)

    account_name = event['account_name']
    account_email = event['account_email']
    account_role = event['account_role']
    template_file = event['template_file']
    stack_name = event['stack_name']
    stack_region = event['stack_region']
    access_to_billing = event['access_to_billing']
    organization_unit_id = event['organization_unit_id']
    account_id = event['account_id']

    account_list = get_account_list()
    print(account_list)

    if account_name in account_list.values():
        print(str(account_name) + "Account already exist")
        print(1)

        for k, v in account_list.items():
            if account_name == v:
                print(k)
                account_id = k
                print(account_id)

    else:
        print("Creating new account: " +
              account_name + " (" + account_email + ")")
        account_id = create_account(
            account_name, account_email, account_role, access_to_billing, organization_unit_id, scp)
        # Comment the above line and uncomment the below line to skip account creation and just test Cfn deployment (for testing)
        # account_id = "481608673808"
        print("Created acount: " + account_id)

    credentials = assume_role(account_id, account_role)
    print("Deploying resources from " + template_file +
          " as " + stack_name + " in " + stack_region)
    template = get_template(template_file)
    stack = deploy_resources(credentials, template, stack_name, stack_region)

    print("Started resource deployment for account " + account_id +
          " (" + account_email + ")" + " from template ")

    return("Started resource deployment for account " + account_id +
           " (" + account_email + ")" + " from template ")
