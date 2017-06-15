''' '''
import os

from oauth2client import client
# import googleapiclient
import httplib2
from apiclient.discovery import build

CLIENT_ID = os.environ['GOOGLE_OAUTH_CLIENT_ID']
CLIENT_SECRET = os.environ['GOOGLE_OAUTH_CLIENT_SECRET']
REDIRECT_URI = os.environ['GOOGLE_OAUTH_REDIRECT_URI']

def get_credentials(user):
    ''' user = user object '''
    access_token = None # credentials['access_token']
    refresh_token = user['googleRefreshToken']
    token_expiry = None # credentials['expires_in'] # Should this be calculated to an epoch time?
    token_uri = 'https://www.googleapis.com/oauth2/v4/token'
    user_agent = None

    return client.GoogleCredentials(access_token,
                                                 CLIENT_ID,
                                                 CLIENT_SECRET,
                                                 refresh_token,
                                                 token_expiry,
                                                 token_uri,
                                                 user_agent,
                                                 revoke_uri='https://accounts.google.com/o/oauth2/revoke',
    )


def get_service(user, service, version='v1'):
    credentials = get_credentials(user)

    http = credentials.authorize(httplib2.Http())

    return build(service, version, http=http)