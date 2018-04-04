
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

aws cognito-idp admin-initiate-auth --user-pool-id <userpool id> --client-id <client_id> --auth-flow ADMIN_NO_SRP_AUTH --auth-parameters USERNAME=<username>,PASSWORD=<password>

aws cognito-idp admin-respond-to-auth-challenge --user-pool-id <userpool id> --client-id <client_id> --challenge-name NEW_PASSWORD_REQUIRED --challenge-responses NEW_PASSWORD=<password>,USERNAME=<username> --session <session id from above command output>

Users should have status confirmed after running above commands.

![](images/Picture8.png)


