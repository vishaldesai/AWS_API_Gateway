
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







