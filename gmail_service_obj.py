'''builds service object from credentials for use in other files
NOTE assumes user's credentials are in the db and up to date. 
NOTE: used sorted() to get the most recent entry - might not be foolproof'''
from pprint import pprint
import httplib2

from apiclient.discovery import build
import oauth2client

# database
from utils.db_vars import *

from gmail_new_user_server import CLIENTSECRETS_LOCATION, SCOPES
CLIENT_SECRET = '691727597265-pgjisvia3glrfa5i4ouq2t9h4ngc5lpj.apps.googleusercontent.com'
CLIENT_ID = '1ensVwuO_p9q5tfOp7B53iCK'

def get_user_creds_from_db(user_email):
    ''' note that elsewhere we use user_id to refer to user_email 
    but gmail uses it's own user_id so I've called is user_email to be clear
    NOTE: converts from db cursor object to normal object'''
    creds_list = db.creds.find({'creds.id_token.email': user_email})
    creds_list = [cred for cred in creds_list]
    # there may be more than one set of credentials found. if so - take the most recent.
    creds_list_sorted = sorted(creds_list, key=lambda k: k['creds']['token_expiry'], reverse=True)
    creds = creds_list_sorted[0]['creds']
    return creds

# def build_service(credentials):
#     """Build a Gmail service object:
#     Args: credentials: OAuth 2.0 credentials.
#     Returns: Gmail service object.
#     """
#     # TODO the below as no mention of refresh token vs access token...
#     # TODO is this already refreshing or is extra code required?  
#     http = httplib2.Http()
#     # http = credentials.authorize(http)  # <<< THIS NEEDS TO WORK
#     flow = flow_from_clientsecrets(CLIENTSECRETS_LOCATION, ' '.join(SCOPES))
#     http = flow.authorize(http)
#     service = build('gmail', 'v1', http=http)
#     return service

def rebuild_credentials_from_db_creds(creds):
    '''takes user credentials from database and returns an 
    Oauth2client object ready for building the service object.
    NOTE: We are REBUILDING credentials class instance as 
    we had to turn it into a dict to put it into the database.
    NOTE: copied from Martin's code. He had all but the refresh token commented out...'''
    access_token = creds['access_token']
    refresh_token = creds['refresh_token']
    token_expiry = creds['token_expiry']
    token_uri = 'https://www.googleapis.com/oauth2/v4/token' # TODO not sure why this is the URL
    user_agent = None
    revoke_uri='https://accounts.google.com/o/oauth2/revoke', # TODO not sure why this is the revokeURI

    credentials = oauth2client.client.GoogleCredentials(
                                                            access_token,
                                                            CLIENT_ID,
                                                            CLIENT_SECRET,
                                                            refresh_token,
                                                            token_expiry,
                                                            token_uri,
                                                            user_agent,
                                                            revoke_uri
    )
    return credentials

def get_service_martin(credentials, service='gmail', version='v1'): # NOTE service here is something else, ignore it?
    ''' builds service object using creds (from db) and get_credentials
    this function authorizes a service object with google so that you can use it to make calls'''
    # authorize the credentials (refresh token or something? I don't know. This is the thing that was missing in Google's own code.)
    http = credentials.authorize(httplib2.Http())
    # build service object using the authorised 'http'
    service = build(service, version, http=http)
    # for some reason this works.
    return service

def main():
    creds = get_user_creds_from_db('agdfoster@gmail.com')
    # pprint(creds, depth=2)
    # re-build credentials object from the Json-like mongo db object
    credentials = rebuild_credentials_from_db_creds(creds)
    # build service object by authorizing credentials with Google
    service = get_service_martin(credentials)
    print(service)
    return service