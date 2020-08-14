import os

"""
IAM_AUTHORIZER:
Use IAM service for authentication, authorization
and request signing. This is used by all AWS services and SDKs.
It can do request over all users

CUSTOM:
Use a built-in authorizer based on ApiKey and Secret Key to authorize users
It can only do request over user logged in
"""
AUTHORIZER: str = os.getenv('AUTHORIZER', 'CUSTOM')
