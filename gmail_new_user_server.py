''' FLASK app that collects signups and populates the database'''
# Flask boilerplate
from flask import Flask
from flask import request
app = Flask(__name__)

import logging
import httplib2
import json
from pprint import pprint
from datetime import datetime

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from apiclient.discovery import build

# database
from utils.db_vars import *

CLIENTSECRETS_LOCATION = 'client_id_2.JSON'
REDIRECT_URI = os.environ['REDIRECT_URI'] # this is NOT the Google redirect URI. I don't get it either.
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/gmail.modify'
    # Add other requested scopes.
]

class GetCredentialsException(Exception):
  """Error raised when an error occurred while retrieving credentials.

  Attributes:
    authorization_url: Authorization URL to redirect the user to in order to
                       request offline access.
  """

  def __init__(self, authorization_url):
    """Construct a GetCredentialsException."""
    self.authorization_url = authorization_url

class CodeExchangeException(GetCredentialsException):
  """Error raised when a code exchange has failed."""


class NoRefreshTokenException(GetCredentialsException):
  """Error raised when no refresh token has been found."""


class NoUserIdException(Exception):
  """Error raised when no user ID could be retrieved."""

# @app.route('/oauth-redirect-uri', methods=['GET'])
def show_html_to_user():
    pass

def exchange_code(authorization_code):
    """Exchange an authorization code for OAuth 2.0 credentials.

    Args:
    authorization_code: Authorization code to exchange for OAuth 2.0
                        credentials.
    Returns:
    oauth2client.client.OAuth2Credentials instance.
    Raises:
    CodeExchangeException: an error occurred.
    """
    flow = flow_from_clientsecrets(CLIENTSECRETS_LOCATION, ' '.join(SCOPES))
    flow.redirect_uri = REDIRECT_URI
    try:
        credentials = flow.step2_exchange(authorization_code)
        return credentials
    except FlowExchangeError as error:
        logging.error('An error occurred: %s', error)
        raise CodeExchangeException(None)

def get_user_info(credentials):
  """Send a request to the UserInfo API to retrieve the user's information.

  Args:
    credentials: oauth2client.client.OAuth2Credentials instance to authorize the
                 request.
  Returns:
    User information as a dict.
  """
  user_info_service = build(
      serviceName='oauth2', version='v2',
      http=credentials.authorize(httplib2.Http()))
  user_info = None
  try:
    user_info = user_info_service.userinfo().get().execute()
  except errors.HttpError as e:
    logging.error('An error occurred: %s', e)
  if user_info and user_info.get('id'):
    return user_info
  else:
    raise NoUserIdException()

def get_authorization_url(email_address, state):
  """Retrieve the authorization URL.

  Args:
    email_address: User's e-mail address.
    state: State for the authorization URL.
  Returns:
    Authorization URL to redirect the user to.
  """
  flow = flow_from_clientsecrets(CLIENTSECRETS_LOCATION, ' '.join(SCOPES))
  flow.params['access_type'] = 'offline'
  flow.params['approval_prompt'] = 'force'
  flow.params['user_id'] = email_address
  flow.params['state'] = state
  return flow.step1_get_authorize_url(REDIRECT_URI)

def get_tokens_using_auth_code(authorization_code, state): # called get_credentials in example https://developers.google.com/gmail/api/auth/web-server
  """Retrieve credentials using the provided authorization code.

  This function exchanges the authorization code for an access token and queries
  the UserInfo API to retrieve the user's e-mail address.
  If a refresh token has been retrieved along with an access token, it is stored
  in the application database using the user's e-mail address as key.
  If no refresh token has been retrieved, the function checks in the application
  database for one and returns it if found or raises a NoRefreshTokenException
  with the authorization URL to redirect the user to.

  Args:
    authorization_code: Authorization code to use to retrieve an access token.
    state: State to set to the authorization URL in case of error.
  Returns:
    oauth2client.client.OAuth2Credentials instance containing an access and
    refresh token.
  Raises:
    CodeExchangeError: Could not exchange the authorization code.
    NoRefreshTokenException: No refresh token could be retrieved from the
                             available sources.
  """
  email_address = ''
  try:
    # exchange auth code for tokens
    credentials = exchange_code(authorization_code)
    # get a few more details
    user_info = get_user_info(credentials)
    email_address = user_info.get('email')
    user_id = user_info.get('id')
    # return and error handle
    if credentials.refresh_token:
        if user_id:
            return credentials
    else:
        credentials = get_stored_credentials(user_id)
        if credentials and credentials.refresh_token:
            return credentials
  except CodeExchangeException as error:
      logging.error('An error occurred during code exchange.')
      # Drive apps should try to retrieve the user and credentials for the current
      # session.
      # If none is available, redirect the user to the authorization URL.
      # error.authorization_url = get_authorization_url(email_address, state) # TODO TURN THIS BACK ON
      raise error
  except NoUserIdException:
      logging.error('No user ID could be retrieved.')
      # No refresh token has been retrieved.

def put_token_in_db(credentials):
    """Store OAuth 2.0 credentials in the application's database.

    This function stores the provided OAuth 2.0 credentials using the user ID as
    key.

    Args:
    user_id: User's ID.
    credentials: OAuth 2.0 credentials to store.
    Raises:
    NotImplemented: This function has not been implemented.
    """
    user_info = get_user_info(credentials)
    email_address = user_info.get('email')
    user_id = user_info.get('id')

    # Credentials come in a special object
    # To retrieve a Json representation of the credentials instance, call the credentials.to_json() method.
    # then convert to dict
    creds = credentials.to_json()
    creds = json.loads(creds)

    db.user_creds.insert({
        'user_info': user_info,
        'user_id': user_id,
        'user_email':email_address,
        'creds': creds,
        # 'credentials': credentials # this maintains attriutes of the class object
        # 'datetime': datetime.now() # for easier access / duplicate removal
    })
    
    return


@app.route("/")
def get_and_store_tokens():
    ''' get URL parameters and return to the main program 
    flask function 'returns' directly the page'''
    # this function is called when a user authorises the app.
    # the auth code is in the URL
    # 1. get the auth code params from the URL
    state = request.args.get('state')
    code = request.args.get('code')
    # 2. now ask Google for tokens
    # NOTE still don't know what state is.
    credentials = get_tokens_using_auth_code(code, state)
    # store creds in db
    put_token_in_db(credentials)
    
    # the return is just what is handed to the page - give it the html you want it to have.
    return '<h1>Connection Successful</h1>'


if __name__ == '__main__':
    app.run()