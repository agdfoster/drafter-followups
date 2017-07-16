'''builds service object from credentials for use in other files
NOTE assumes user's credentials are in the db and up to date. 
NOTE: used sorted() to get the most recent entry - might not be foolproof
THIS IS THE VERSION CREATED SO IT WORKS FOR ANY USER NOT THE LOCAL QUICKSTART ONE'''
from pprint import pprint
import httplib2

from apiclient.discovery import build
# import googleapiclient
import oauth2client
import logging

# database
from utils.db_vars import *

# USER = 'foster@draft-ai.com' # THIS SHOULD BE THE ONLY PLACE THIS VARIABLE IS STORED - IT IS TEMPORARY

CLIENT_SECRET = os.environ['GOOGLE_OAUTH_CLIENT_SECRET']
CLIENT_ID = os.environ['GOOGLE_OAUTH_CLIENT_ID']

def get_user_creds_from_db(user_email):
    ''' note that elsewhere we use user_id to refer to user_email 
    but gmail uses it's own user_id so I've called is user_email to be clear
    NOTE: converts from db cursor object to normal object
    NOTE: the email returned is 100% the email that the client should then be querying'''
    creds_list = db.user_creds.find({'creds.id_token.email': user_email})
    creds_list = [cred for cred in creds_list]
    if creds_list == []:
        raise ValueError('Alex, This user was not found in the database!!')
    # there may be more than one set of credentials found. if so - take the most recent.
    creds_list_sorted = sorted(creds_list, key=lambda k: k['creds']['token_expiry'], reverse=True)
    creds = creds_list_sorted[0]['creds']
    fname = creds_list_sorted[0]['user_info']['given_name']
    sname = creds_list_sorted[0]['user_info']['family_name']
    email = creds_list_sorted[0]['user_info']['email']
    return creds, fname, sname, email

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

def rebuild_credentials_object_from_db_creds(creds):
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

def get_service_martin(credentials): # NOTE service here is something else, ignore it?
    ''' builds service object using creds (from db) and get_credentials
    this function authorizes a service object with google so that you can use it to make calls
    NOTE: These credentials should ALREADY be refreshed by this point.'''
    
    # error definitions
    def credentials_error():
        logging.warning('An error occurred: %s' % error)
        if error.resp.status == 401:
            # Credentials have been revoked.
            logging.warning('credentials have probably been revoked - send user the below URL')
            url = gmail_new_user_server.get_authorization_url(email, True)
            logging.warning(url)
    # authorize credentials
    # try:
    http = credentials.authorize(httplib2.Http())
    # except errors.HttpError as error:
        # credentials_error()
    # refresh token
    # credentials.refresh(http) # TODO FUCK YOU REFRESH TOKEN
    # build service object using the authorised 'http'
    service = build('gmail', 'v1', http=http)
    # for some reason this works.
    return service

'''
OK REFRESH TOKEN
Evidence:
1. Works without refresh request, breaks with it
2. Internet says (I think) that it should refresh without specifically calling .request
3. Access seems to expire after a short while, few hours.
4. Both the URL AND the auth URL seem to expire. Auth URL still loads but doesn't work.
5. I have set the product name and name to be the same in the Google console
Ideas:
1. Create totally new project on Google console and re plug
2. The auth page expiring could be linked to the true problem, wait for that to happen then fix it without regenerating. SHOULD the auth link expire?
3. Could be linked to two factor authentication? Try on foster@draft-ai.com
4. Could have something to do with that State param you bodged

5. URL is bad... but this looks right checking against https://www.themarketingtechnologist.co/google-oauth-2-enable-your-application-to-access-data-from-a-google-user/
URL = https://accounts.google.com/o/oauth2/auth?client_id=691727597265-pgjisvia3glrfa5i4ouq2t9h4ngc5lpj.apps.googleusercontent.com&
    edirect_uri=http%3A%2F%2Flocalhost%3A5000&
    scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fgmail.readonly+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fuserinfo.email+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fuserinfo.profile+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fgmail.modify&
    access_type=offline&
    response_type=code&
    approval_prompt=force'
6. Look at that Oauth example you've saved here

HM, OK... so refresh token seems to be lasting now.
BUT the auth URL is still breaking after time.... AHA but it's the same every time right?
... so that's just because I'm pressing back rather than re-using the URL. Stupid Alex.
1. Waiting on test for this.

TESTING WITH FOSTER@DRAFT-AI.COM
1. need way to know which accounts emails it's polling.
'''


def main(user_email):
    # get user creds from db
    logging.info('acquiring credentials for {}'.format(user_email))
    creds, fname, sname, email = get_user_creds_from_db(user_email)
    logging.info('acquiring credentials complete for {}'.format(user_email))
    # pprint(creds, depth=2)
    
    # re-build credentials object from the Json-like mongo db object
    logging.info('rebuilding credentials for {}'.format(user_email))
    credentials = rebuild_credentials_object_from_db_creds(creds)
    logging.info('rebuilding credentials complete for {}'.format(user_email))
    
    # build service object by authorizing credentials with Google
    logging.info('building service object for {}'.format(user_email))
    service = get_service_martin(credentials)
    logging.info('building service object complete for {}'.format(user_email))

    return service, fname, sname, email

if __name__ == '__main__':
    main('foster@draft-ai.com')
    print('building service object seemed to work')