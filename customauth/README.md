
API Gateway support Cognito OAuth scopes for method level authorization. A scope defines the level of access to a resource that an application has permission to. In this document we are presenting authentication and authorization solution for API Gateway using custom authorizer. Lambda custom authorization will validate OAuth scopes and Cognito username/password for applications that does not support OAuth scopes. After validation based on authorization metadata in Dynamo DB it will allow API invoker to call specific method/resource. 

# Solution

![](images/Picture1.png)
![](images/Picture2.png)
