''' THIS IS DEPRECATED '''
# import logging
# from oauth2client.client import flow_from_clientsecrets
# from oauth2client.client import FlowExchangeError
# from apiclient.discovery import build

# CLIENTSECRETS_LOCATION = 'client_id_2.JSON'
# REDIRECT_URI = 'http://localhost:5000' #'<YOUR_REGISTERED_REDIRECT_URI>' # http://www.drafterhq.com?
# # ^^^ When you create a client ID in the Google API Console, two redirect_uri parameters are created for you: urn:ietf:wg:oauth:2.0:oob and http://localhost. The value your application uses determines how the authorization code is returned to your application.
# SCOPES = [
#     'https://www.googleapis.com/auth/gmail.readonly',
#     'https://www.googleapis.com/auth/userinfo.email',
#     'https://www.googleapis.com/auth/userinfo.profile',
#     'https://www.googleapis.com/auth/gmail.modify'
#     # Add other requested scopes.
# ]

# def get_authorization_url(email_address, state):
#     """Retrieve the authorization URL.
#     Args:
#         email_address: User's e-mail address.
#         state: State for the authorization URL.
#     Returns:
#         Authorization URL to redirect the user to."""
#     flow = flow_from_clientsecrets(CLIENTSECRETS_LOCATION, ' '.join(SCOPES), redirect_uri=REDIRECT_URI)
#     flow.params['access_type'] = 'offline'
#     flow.params['approval_prompt'] = 'force'
#     flow.params['user_id'] = email_address
#     flow.params['state'] = state
#     return flow.step1_get_authorize_url() # got this error: step1_get_authorize_url() takes at most 1 positional argument (2 given). The redirect_uri parameter for OAuth2WebServerFlow.step1_get_authorize_url is deprecated. Please move to passing the redirect_uri in via the constructor.


# if __name__ == '__main__':
#     # first we need the URL to send the user to
#     auth = get_authorization_url('agdfoster@gmail.com', True) #arbritrarily set to True, not sure what state is.
#     print(auth)