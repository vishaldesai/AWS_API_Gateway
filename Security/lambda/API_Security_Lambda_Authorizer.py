from __future__ import print_function

import re
import time
import pprint
import json


def lambda_handler(event, context):

    if event['authorizationToken'] == "aws" :
     var1 = '''{"principalId": "user|a1b2c3d4", "policyDocument": { "Version": "2012-10-17",  "Statement": [ { "Action": "execute-api:Invoke", "Effect": "Allow", "Resource": [ "arn:aws:execute-api:us-east-1:084009911244:l4y1rtmoi5/*/GET/awscloud" ] } ] },  "context": { "key": "value", "number": 1, "bool": true } }'''
     var2 = json.loads(var1)

    return var2
