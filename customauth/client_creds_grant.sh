#!/usr/bin/env bash

#===============================================================================
# CLIENT CREDENTIALS GRANT
#===============================================================================

## Set constants ##
AUTH_DOMAIN="MYDOMAIN.auth.REGION.amazoncognito.com" # Update MYDOMAIN and REGION
CLIENT_ID="xxxxxxxxxxxxxxxxxxxxxxxxx" # Replace with app client ID
CLIENT_SECRET="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" # Replace with app client secret
GRANT_TYPE="client_credentials"

## Get access token from /oauth2/token endpoint ##
authorization="$(printf "${CLIENT_ID}:${CLIENT_SECRET}" \
                    | base64 \
                    | tr -d "\n"
                )"
curl "https://${AUTH_DOMAIN}/oauth2/token" \
    -H "Authorization: Basic ${authorization}" \
    -d "grant_type=${GRANT_TYPE}"
