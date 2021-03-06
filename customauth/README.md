
API Gateway support Cognito OAuth scopes for method level authorization. A scope defines the level of access to a resource that an application has permission to. In this document we are presenting authentication and authorization solution for API Gateway using custom authorizer. Lambda custom authorization will validate OAuth scopes and Cognito username/password for applications that does not support OAuth scopes. After validation based on authorization metadata in Dynamo DB it will allow API invoker to call specific method/resource. 

## Solution

![](images/Picture1.png)
![](images/Picture2.png)

### Create Cognito User Pool

Enter pool name and click on Step through settings. Accept default until you reach Review section and then Click on create pool.

![](images/Picture3.png)

Create domain.

![](images/Picture4.png)

Create Resource server

![](images/Picture5.png)

Click on App clients.

![](images/Picture6.png)

Create two application users and authenticate them using AWS CLI commands as shown below.

![](images/Picture7.png)

*aws cognito-idp admin-initiate-auth --user-pool-id <userpool id> --client-id <client_id> --auth-flow ADMIN_NO_SRP_AUTH --auth-parameters USERNAME=<username>,PASSWORD=<password>*

*aws cognito-idp admin-respond-to-auth-challenge --user-pool-id <userpool id> --client-id <client_id> --challenge-name NEW_PASSWORD_REQUIRED --challenge-responses NEW_PASSWORD=<password>,USERNAME=<username> --session <session id from above command output>*

Users should have status confirmed after running above commands.

![](images/Picture8.png)


### Create Lambda function for API custom authorizer.

Use code from Appendix A4

### Create table in DyanmoDB and update authorization metadata.

![](images/Picture9.png)

Policy document in appendix A5.

### API Gateway Setup

Create new Authorizer for API Gateway using lambda function created in previous step.

![](images/Picture10.png)

### Testing:

Cognito User is authorized to call read/GET resource/method.

![](images/Picture11.png)
![](images/Picture12.png)

Cognito App client id is authorized to call write/POST resource/method.

![](images/Picture13.png)
![](images/Picture14.png)

## Appendix:

### A1. Sample Terraform to create Cognito resources.

File: varibles.tf

```
variable "aws_region" {
  description = "AWS region to launch servers."
  default     = "us-east-1"
}


variable "create_resource_server_file" {
  description = "json input for create resource server"
  default     = "file:///Users/username/Downloads/terra/create-resource-server.json"
}

variable "create_user_pool_client_file" {
  description = "json input for create resource server"
  default     = "file:///Users/username/Downloads/terra/create-user-pool-client.json"
}
```

File: main.tf

```
provider "aws" {
   region = "${var.aws_region}"
}

resource "aws_cognito_user_pool" "pool" {
  name = "mycognitopool1"
}


resource "null_resource" "aws_cognito_create_resource_server" {
provisioner "local-exec" {
    command = <<EOF
    aws cognito-idp create-resource-server --user-pool-id ${aws_cognito_user_pool.pool.id} --cli-input-json ${var.create_resource_server_file}
    EOF
    }
}

resource "aws_cognito_user_pool_domain" "main" {
  domain = "mycogpool1"
  user_pool_id = "${aws_cognito_user_pool.pool.id}"
}


resource "null_resource" "aws_cognito_create_user_pool_client" {
provisioner "local-exec" {
    command = <<EOF
    aws cognito-idp create-user-pool-client --user-pool-id ${aws_cognito_user_pool.pool.id} --cli-input-json ${var.create_user_pool_client_file}
    EOF
    }
}
```

File: create-user-pool-client.json

```
{
    "UserPoolId": "",
    "ClientName": "validate",
    "GenerateSecret": false,
    "RefreshTokenValidity": 0,
    "ExplicitAuthFlows": [
        "ADMIN_NO_SRP_AUTH",
        "USER_PASSWORD_AUTH"
    ],
    "SupportedIdentityProviders": [
        "COGNITO"
    ],
    "CallbackURLs": [
        "https://validate.com/"
    ],
    "LogoutURLs": [
        "https://validate.com/"
    ],
    "AllowedOAuthFlows": [
        "code"
    ],
    "AllowedOAuthScopes": [
        "https://resource1/get",
        "https://resource1/post"
    ],
    "AllowedOAuthFlowsUserPoolClient": true
}
```

File: create-resource-server.json

```
{
    "UserPoolId": "",
    "Identifier": "https://resource1",
    "Name": "resource",
    "Scopes": [
        {
            "ScopeName": "get",
            "ScopeDescription": "allow gets"
        },
        {
            "ScopeName": "post",
            "ScopeDescription": "allow posts"
        }
    ]
}
```

### A2. API Gateway Swagger template

```
---
swagger: "2.0"
info:
  version: "2018-03-21T17:11:25Z"
  title: "Security_CognitoOAuthScopes1"
host: "3lgc533c.execute-api.us-east-1.amazonaws.com"
basePath: "/dev"
schemes:
- "https"
paths:
  /read:
    get:
      consumes:
      - "application/json"
      produces:
      - "application/json"
      parameters:
      - name: "access_token"
        in: "query"
        required: false
        type: "string"
      - name: "password"
        in: "query"
        required: false
        type: "string"
      - name: "username"
        in: "query"
        required: false
        type: "string"
      responses:
        200:
          description: "200 response"
          schema:
            $ref: "#/definitions/Empty"
      security:
      - customv1: []
      x-amazon-apigateway-integration:
        responses:
          default:
            statusCode: "200"
        requestParameters:
          integration.request.querystring.password: "method.request.querystring.password"
          integration.request.querystring.access_token: "method.request.querystring.access_token"
          integration.request.querystring.username: "method.request.querystring.username"
        uri: "arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/arn:aws:lambda:us-east-1:xxxx:function:HelloRead/invocations"
        passthroughBehavior: "when_no_templates"
        httpMethod: "POST"
        requestTemplates:
          application/json: "{\n    \"access_token\" : \"$input.params('access_token')\"\
            ,\n    \"username\" : \"$input.params('username')\",\n    \"password\"\
            \ : \"$input.params('password')\"\n}"
        contentHandling: "CONVERT_TO_TEXT"
        type: "aws"
  /write:
    post:
      consumes:
      - "application/json"
      produces:
      - "application/json"
      parameters:
      - name: "access_token"
        in: "query"
        required: false
        type: "string"
      - name: "password"
        in: "query"
        required: false
        type: "string"
      - name: "username"
        in: "query"
        required: false
        type: "string"
      responses:
        200:
          description: "200 response"
          schema:
            $ref: "#/definitions/Empty"
      security:
      - customv1: []
      x-amazon-apigateway-integration:
        responses:
          default:
            statusCode: "200"
        requestParameters:
          integration.request.querystring.password: "method.request.querystring.password"
          integration.request.querystring.access_token: "method.request.querystring.access_token"
          integration.request.querystring.username: "method.request.querystring.username"
        uri: "arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/arn:aws:lambda:us-east-1:xxxx:function:HelloWrite/invocations"
        passthroughBehavior: "when_no_templates"
        httpMethod: "POST"
        requestTemplates:
          application/json: "{\n    \"access_token\" : \"$input.params('access_token')\"\
            ,\n    \"username\" : \"$input.params('username')\",\n    \"password\"\
            \ : \"$input.params('password')\"\n}"
        contentHandling: "CONVERT_TO_TEXT"
        type: "aws"
securityDefinitions:
  customv1:
    type: "apiKey"
    name: "Unused"
    in: "header"
    x-amazon-apigateway-authtype: "custom"
    x-amazon-apigateway-authorizer:
      authorizerCredentials: "arn:aws:iam::xxxx:role/service-role/Admintest"
      authorizerUri: "arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/arn:aws:lambda:us-east-1:xxxx:function:cloud9-buildauthorizev2-buildauthorizev2-abc/invocations"
      authorizerResultTtlInSeconds: 0
      type: "request"
definitions:
  Empty:
    type: "object"
    title: "Empty Schema"
```

### A3. Authorization Code Grant Script

```
#!/usr/bin/env bash

#===============================================================================
# CLIENT CREDENTIALS GRANT
#===============================================================================

## Set constants ##
AUTH_DOMAIN="xxxx.auth.us-east-1.amazoncognito.com" # Update MYDOMAIN and REGION
CLIENT_ID="xxxx" # Replace with app client ID
CLIENT_SECRET="xxxx" # Replace with app client secret
GRANT_TYPE="client_credentials"

## Get access token from /oauth2/token endpoint ##
authorization="$(printf "${CLIENT_ID}:${CLIENT_SECRET}" \
                    | base64 \
                    | tr -d "\n"
                )"



curl "https://${AUTH_DOMAIN}/oauth2/token" \
    -H "Authorization: Basic ${authorization}" \
    -d "grant_type=${GRANT_TYPE}"
```

### A4. Lambda for API custom authorizer.

```
import boto3
import requests
import json
import time
from boto3.dynamodb.conditions import Key, Attr
from jose import jwk, jwt
from jose.utils import base64url_decode
from warrant import Cognito
from botocore.exceptions import ClientError

def access_token_validation(token):
    
    # Define region and app userpool id
    region = 'us-east-1'
    userpool_id = 'us-east-1_wekRrmrtl'
    keys_url = 'https://cognito-idp.{}.amazonaws.com/{}/.well-known/jwks.json'.format(region, userpool_id)

    response = requests.get(keys_url)
    keys = json.loads(response.text)['keys']
    
    headers = jwt.get_unverified_headers(token)

    kid = headers['kid']

    # search for the kid in the downloaded public keys
    key_index = -1
    for i in range(len(keys)):
        if kid == keys[i]['kid']:
            key_index = i
            break

    if key_index == -1:
        print('Public key not found in jwks.json');
        return False

    # construct the public key
    public_key = jwk.construct(keys[key_index])
    # get the last two sections of the token,
    # message and signature (encoded in base64)
    message, encoded_signature = str(token).rsplit('.', 1)
    # decode the signature
    decoded_signature = base64url_decode(encoded_signature.encode())

    # verify the signature
    if not public_key.verify(message.encode(), decoded_signature):
        return False
    else:
        return jwt.get_unverified_claims(token)
    

def lambda_handler(event, context):
    print(event)
    for key,value in event.items():
        if key == "queryStringParameters":
            access_token = value.get('access_token') 
            username = value.get('username')
            password = value.get('password')

    print("1")
    if access_token is not None:
        print("2")
        try:
            token_claims=access_token_validation(access_token)
            client_id = token_claims.get('client_id')
            scope     = token_claims.get('scope')
        except ClientError as e:
            print(e)
            raise Exception('Unauthorized token')

        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.Table('customauthorizer')

        try:
            response = table.query(
                KeyConditionExpression=Key('id').eq(client_id) & Key('scope').eq(scope)
            )
            print("3")
            for i in response['Items']:
                policydoc=json.loads(i['policydoc'])
                return policydoc
        except ClientError as e:
            print(e)

            
    elif ( username is not None and password is not None ):
        
        u = Cognito('us-east-1_wekRrmrtl','6b25dg5amg6eqjl3h6aab5t601',  username=username)
    
        try:
            u.authenticate(password=password)
        except ClientError as e:
            print(e)
            raise Exception('Unauthorized username/password')
        
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.Table('customauthorizer')
        
        try:
            response = table.query(
                KeyConditionExpression=Key('id').eq(username)
                )

            for i in response['Items']:
                policydoc=json.loads(i['policydoc'])
                return policydoc
                    
        except ClientError as e:
            print(e)
            
        
    else:
        print("Provide username/password or access_token")
```            
        
## A5. Policy Document

```
{
  "principalId": "user|a1b2c3d4",
  "policyDocument": {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Action": "execute-api:Invoke",
        "Effect": "Allow",
        "Resource": [
          "arn:aws:execute-api:us-east-1:xxx:3lgc5v3c/*/POST/write"
        ]
      }
    ]
  },
  "context": {
    "key": "value",
    "number": 1,
    "bool": true
  }
}
```









