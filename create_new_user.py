''' '''
import logging
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from apiclient.discovery import build

CLIENTSECRETS_LOCATION = 'client_id_2.JSON'
REDIRECT_URI = '<YOUR_REGISTERED_REDIRECT_URI>'
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/gmail.modify'
    # Add other requested scopes.
]

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


if __name__ == '__main__':
    # first we need the URL to send the user to
    get_authorization_url('agdfoster@gmail.com', True)