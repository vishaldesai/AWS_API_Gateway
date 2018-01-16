import sys
import json
import os
import boto3
import time

api_name   = sys.argv[1]
input_file = sys.argv[2]
region     = sys.argv[3]

def get_template(template_file):

    print("Reading resources from " + template_file)
    head, tail = os.path.split(template_file)
    template_file1 = tail
    s3 = boto3.resource('s3')
    obj = s3.Object('vishaldxc', template_file1)
    cf_template = obj.get()['Body'].read().decode('utf-8')
    return cf_template



client = boto3.client('apigateway',region)


response = client.create_rest_api(
    name=api_name,
    endpointConfiguration={
        'types': [
            'EDGE',
        ]
    }
)

for key,value in response.items():
    if key == 'id':
            api_id = value


time.sleep(5)
swaggercontent = get_template(input_file)

response = client.put_rest_api(
    restApiId=api_id,
    mode='overwrite',
    failOnWarnings=False,
    body=swaggercontent,
)

print(response)



