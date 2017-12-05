import base64
import boto3

def encrypt(texttoencrypt):
    #Replace empty string with master key below from KMS
    boto_master_key_id = ''
    kms = boto3.client('kms', region_name='us-east-1')
    stuff = kms.encrypt(KeyId=boto_master_key_id,Plaintext=texttoencrypt)
    binary_encrypted = stuff[u'CiphertextBlob']
    encrypted_password = base64.b64encode(binary_encrypted)
    return encrypted_password.decode()
    #return encrypted_password

def dynamodbupdate(account_name_column,account_name_value,other_column,other_value):
    dynamodb=boto3.resource('dynamodb')
    table=dynamodb.Table('credentials')
    response = table.update_item(
        Key={
            account_name_column: account_name_value
            },
                UpdateExpression="set #column = :value",
                ExpressionAttributeNames={
                        '#column': other_column
                        },
                ExpressionAttributeValues={
                    ':value': other_value
                        },
                ReturnValues="UPDATED_NEW"
            )


def lambda_handler(event, context):
    # TODO implement
    #boto_master_key_id = event['key_id']

    for key,value in event.items(): #this gives you both
        print(key,value)
        if key == 'account_name':
            account_name_column = key
            account_name_value = value
        else:
            other_column = key
            other_value = encrypt(value)
            dynamodbupdate(account_name_column,account_name_value,other_column,other_value)
