"""Test the Vercel handler locally"""

import json
from api.index import handler

# Test 1: Basic GET request
print("Test 1: Basic GET request")
request1 = {
    'method': 'GET',
    'path': '/health',
    'headers': {}
}
result1 = handler(request1)
print(f"Status: {result1['statusCode']}")
print(f"Body: {result1['body']}")
print()

# Test 2: With bearer token (if set)
print("Test 2: With bearer token")
import os
token = os.environ.get("SERVER_BEARER_TOKEN", "")
if token:
    request2 = {
        'method': 'GET',
        'path': '/health',
        'headers': {'Authorization': f'Bearer {token}'}
    }
    result2 = handler(request2)
    print(f"Status: {result2['statusCode']}")
    print(f"Body: {result2['body']}")
else:
    print("SERVER_BEARER_TOKEN not set, skipping bearer token test")
print()

# Test 3: Without bearer token when required
print("Test 3: Without bearer token (should fail if token is required)")
os.environ["SERVER_BEARER_TOKEN"] = "test_token_123"
# Reload the module to get new token
import importlib
import api.index
importlib.reload(api.index)
from api.index import handler as handler_with_token

request3 = {
    'method': 'GET',
    'path': '/health',
    'headers': {}
}
result3 = handler_with_token(request3)
print(f"Status: {result3['statusCode']}")
print(f"Body: {result3['body']}")
print()

print("All tests completed!")

