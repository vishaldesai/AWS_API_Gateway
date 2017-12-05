import base64
import boto3
import json

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

def decrypt(texttodecrypt):
    kms = boto3.client('kms', region_name='us-east-1')
    binary_encrypted = base64.b64decode(texttodecrypt)
    #stuff = kms.decrypt(CiphertextBlob=binary_encrypted)
    stuff = kms.decrypt(CiphertextBlob=binary_encrypted)
    #Replace empty string with master key below from KMS
    if stuff[u'KeyId'] == '':
        plaintext = stuff[u'Plaintext']
        return plaintext.decode()
    else:
        return null


def dynamodbquery(account_name):
    dynamodb=boto3.resource('dynamodb')
    table=dynamodb.Table('credentials')
    response = table.get_item(
        Key={
            'account_name': account_name
        }
    )

    return response


def lambda_handler(event, context):
    # TODO implement
    row = dynamodbquery(event['account_name'])
    account_dict = {}
    for key,value in row.items(): #this gives you both
        for key1,value1 in value.items():
            #print(key1,value1)

            if key1 == 'account_name':
                #print('account_name: ' + value1)
                account_dict[key1] = value1
            elif key1 in ('RequestId','HTTPStatusCode','HTTPHeaders','RetryAttempts'):
                pass
            else:
                decryptvalue = decrypt(value1)
                #print(key1 + ': ' + decryptvalue)
                account_dict[key1] = decryptvalue



    #print(account_dict)

    credentials = assume_role(account_dict['account_id'], account_dict['account_role'])

    client=boto3.client('ec2',aws_access_key_id=credentials['AccessKeyId'],
                          aws_secret_access_key=credentials['SecretAccessKey'],
                          aws_session_token=credentials['SessionToken'],
                          region_name='us-east-1')
    response = client.describe_instances()
    print(response)
