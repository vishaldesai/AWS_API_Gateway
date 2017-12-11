

# AWS Version 4 signing example

# EC2 API (DescribeRegions)

# See: http://docs.aws.amazon.com/general/latest/gr/sigv4_signing.html
# This version makes a GET request and passes the signature
# in the Authorization header.
import boto3
import sys, os, base64, datetime, hashlib, hmac, urllib
import requests # pip install requests

# ************* REQUEST VALUES *************
method = 'GET'
service = 'execute-api'
host = 'n292bq55ke.execute-api.us-east-1.amazonaws.com'
region = 'us-east-1'
endpoint = 'https://n292bq55ke.execute-api.us-east-1.amazonaws.com/prod'
request_parameters = ''


# Key derivation functions. See:
# http://docs.aws.amazon.com/general/latest/gr/signature-v4-examples.html#signature-v4-examples-python
def sign(key, msg):
    return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

def getSignatureKey(key, dateStamp, regionName, serviceName):
    kDate = sign(('AWS4' + key).encode('utf-8'), dateStamp)
    kRegion = sign(kDate, regionName)
    kService = sign(kRegion, serviceName)
    kSigning = sign(kService, 'aws4_request')
    return kSigning

access_key = '....'
secret_key = '.....'


if access_key is None or secret_key is None:
    print('No access key is available.')
    sys.exit()


# Create a date for headers and the credential string
t = datetime.datetime.utcnow()
amz_date = t.strftime('%Y%m%dT%H%M%SZ') # Format date as YYYYMMDD'T'HHMMSS'Z'
datestamp = t.strftime('%Y%m%d') # Date w/o time, used in credential scope


# ************* TASK 1: CREATE A CANONICAL REQUEST *************
# http://docs.aws.amazon.com/general/latest/gr/sigv4-create-canonical-request.html

# Because almost all information is being passed in the query string,
# the order of these steps is slightly different than examples that
# use an authorization header.

# Step 1: Define the verb (GET, POST, etc.)--already done.

# Step 2: Create canonical URI--the part of the URI from domain to query
# string (use '/' if no path)
canonical_uri = '/prod'

# Step 3: Create the canonical headers and signed headers. Header names
# must be trimmed and lowercase, and sorted in code point order from
# low to high. Note trailing \n in canonical_headers.
# signed_headers is the list of headers that are being included
# as part of the signing process. For requests that use query strings,
# only "host" is included in the signed headers.
canonical_headers = 'host:' + host + '\n'
signed_headers = 'host'

# Match the algorithm to the hashing algorithm you use, either SHA-1 or
# SHA-256 (recommended)
algorithm = 'AWS4-HMAC-SHA256'
credential_scope = datestamp + '/' + region + '/' + service + '/' + 'aws4_request'

# Step 4: Create the canonical query string. In this example, request
# parameters are in the query string. Query string values must
# be URL-encoded (space=%20). The parameters must be sorted by name.

canonical_querystring = 'X-Amz-Algorithm=AWS4-HMAC-SHA256'
canonical_querystring += '&X-Amz-Credential=' + urllib.quote_plus(access_key + '/' + credential_scope)
canonical_querystring += '&X-Amz-Date=' + amz_date
canonical_querystring += '&X-Amz-Expires=86400'
canonical_querystring += '&X-Amz-SignedHeaders=' + signed_headers

# Step 5: Create payload hash. For GET requests, the payload is an
# empty string ("").
payload_hash = hashlib.sha256('').hexdigest()

# Step 6: Combine elements to create create canonical request
canonical_request = method + '\n' + canonical_uri + '\n' + canonical_querystring + '\n' + canonical_headers + '\n' + signed_headers + '\n' + payload_hash


# ************* TASK 2: CREATE THE STRING TO SIGN*************
string_to_sign = algorithm + '\n' +  amz_date + '\n' +  credential_scope + '\n' +  hashlib.sha256(canonical_request).hexdigest()


# ************* TASK 3: CALCULATE THE SIGNATURE *************
# Create the signing key
signing_key = getSignatureKey(secret_key, datestamp, region, service)

# Sign the string_to_sign using the signing_key
signature = hmac.new(signing_key, (string_to_sign).encode("utf-8"), hashlib.sha256).hexdigest()


# ************* TASK 4: ADD SIGNING INFORMATION TO THE REQUEST *************
# The auth information can be either in a query string
# value or in a header named Authorization. This code shows how to put
# everything into a query string.
canonical_querystring += '&X-Amz-Signature=' + signature


# ************* SEND THE REQUEST *************
# The 'host' header is added automatically by the Python 'request' lib. But it
# must exist as a header in the request.
request_url = endpoint + "?" + canonical_querystring

print '\nBEGIN REQUEST++++++++++++++++++++++++++++++++++++'
print 'Request URL = ' + request_url
r = requests.get(request_url)

print '\nRESPONSE++++++++++++++++++++++++++++++++++++'
print 'Response code: %d\n' % r.status_code
print r.text
