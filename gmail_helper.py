"""
Helper for the Gmail API

Note: Google's library relies on httplib2
which is NOT threadsafe
"""

import os
import base64
import logging
import datetime
import email.mime.text
import email.mime.multipart
import email.utils

import bs4
# I believe this is necessary because some of the talon regexes are compiled with regex - can we use just the patterns so we are not reliant upon this?
import regex as re
import retry
import httplib2
import oauth2client
import apiclient
import html2text

# import db_helper
from .text_processing import reply_parser, regexes, preprocess_text
from .utilities import utils


CLIENT_ID = os.environ['GOOGLE_OAUTH_CLIENT_ID']
CLIENT_SECRET = os.environ['GOOGLE_OAUTH_CLIENT_SECRET']
REDIRECT_URI = os.environ['GOOGLE_OAUTH_REDIRECT_URI']


PROJECT_ID = os.environ['GCLOUD_PROJECT']
TOPIC_NAME = 'mail'
FULL_TOPIC_NAME = 'projects/{}/topics/{}'.format(PROJECT_ID, TOPIC_NAME)

logger = logging.getLogger('gmail_helper')
logger.setLevel(logging.WARNING)

handler = logging.StreamHandler()
# handler.setFormatter(formatter)
logger.addHandler(handler)


def get_credentials(user):
    access_token = None # credentials['access_token']
    refresh_token = user['googleRefreshToken']
    token_expiry = None # credentials['expires_in'] # Should this be calculated to an epoch time?
    token_uri = 'https://www.googleapis.com/oauth2/v4/token'
    user_agent = None

    return oauth2client.client.GoogleCredentials(access_token,
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

    return apiclient.discovery.build(service, version, http=http)


def list_history_all(user, start_history_id):
    """List history of all changes to the user's mailbox since a given id

    Returns:
    A list of mailbox changes that occurred after the start_history_id.
    """
    try:
        service = get_service(user, 'gmail')
    except Exception as exc:
        logger.error('Error with %s: %s', user['userEmailAddress'], exc)
        # logger.error(exc)

    history = service.users().history().list(userId='me', startHistoryId=start_history_id).execute()

    changes = history['history'] if 'history' in history else []
    while 'nextPageToken' in history:
        page_token = history['nextPageToken']
        history = service.users().history().list(userId='me', startHistoryId=start_history_id, pageToken=page_token).execute()

        if history.get('history'):
            changes.extend(history['history'])

    if not changes:
        return {}

    return {'history': changes}


def list_history(user, startHistoryId):
    return list_history_all(user, startHistoryId)
    # service = get_service(user, 'gmail')

    # # TODO: What about other optional parameters
    # query = service.users().history().list(userId='me', startHistoryId=startHistoryId)
    # result = query.execute()

    # return result


@retry.retry(tries=2)
def get_message(user, message_id):
    """
    Fetches the message corresponding to the id provided
    """
    service = get_service(user, 'gmail')

    # print('Getting message: "{}" for user {}'.format(message_id, user))

    query = service.users().messages().get(userId='me', id=message_id)
    result = query.execute()

    return result


def get_user_info(user):
  """Send a request to the UserInfo API to retrieve the user's information.

  Args:
    credentials: oauth2client.client.OAuth2Credentials instance to authorize the
                 request.
  Returns:
    User information as a dict.
  """
  # user_info_service = build(
  #     serviceName='oauth2', version='v2',
  #     http=credentials.authorize(httplib2.Http()))

  user_info_service = get_service(user, 'oauth2', version='v2')
  user_info = None

  try:
    user_info = user_info_service.userinfo().get().execute()
  except Exception as exc:
    logging.error('An error occurred: %s', exc)

  if user_info and user_info.get('id'):
    return user_info
  else:
    raise ValueError('No user info gathered')


def get_email_address_from_refresh_token(google_refresh_token):
    temp_user = {'googleRefreshToken': google_refresh_token}

    service = get_service(temp_user, 'gmail')

    # print('Getting message: "{}" for user {}'.format(message_id, user))

    query = service.users().getProfile(userId='me')
    result = query.execute()

    email_address = result.get('emailAddress')

    if not email_address:
        print(result)
        raise ValueError('Error getting email address')

    return email_address


def get_thread(user, thread_id):
    """Fetches the thread corresponding to the id provided"""
    service = get_service(user, 'gmail')

    query = service.users().threads().get(userId='me', id=thread_id)
    result = query.execute()

    return result


def create_mime(sender, to_email, subject, msg_html, msg_plain, thread_id):
    msg = email.mime.multipart.MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = to_email
    msg.attach(email.mime.text.MIMEText(msg_plain, 'plain'))
    msg.attach(email.mime.text.MIMEText(msg_html, 'html'))

    # TODO: Is there a better way to do this?
    base64_encoded_message_string = base64.urlsafe_b64encode(bytes(msg.as_string(), 'utf-8')).decode('utf-8')
    return {'raw': base64_encoded_message_string, 'threadId': thread_id}



def get_message_header(message, header_name):
    headers = message['payload']['headers']
    # import pprint
    # pprint.pprint(headers)

    try:
        value = next(header['value'] for header in headers if header['name'] == header_name)
    except StopIteration:
        logger.warning('Could not find header "%s" in message "%s"', header_name, message['id'])
        return ''

    return value


def send_reply(user, in_reply_to_message_id, body):
    """Send an email

    TODO: Include quoted text

    Arguments:
        user {[type]} -- [description]
        in_reply_to_message_id {[type]} -- [description]
        body {[type]} -- [description]
        subject {[type]} -- [description]
        to {[type]} -- [description]
    """

    previous_message = get_message(user, in_reply_to_message_id)


    to_email = get_message_header(previous_message, 'From')
    sender = user['userEmailAddress']
    subject = 'Re: ' + get_message_header(previous_message, 'Subject')
    msg_html = body
    msg_plain = html2text.html2text(body)
    thread_id = previous_message['threadId']

    mime_formatted_message_string = create_mime(sender, to_email, subject, msg_html, msg_plain, thread_id)


    service = get_service(user, 'gmail')
    query = service.users().messages().send(userId='me', body=mime_formatted_message_string)
    query.execute()


def get_from_person(message):
    """Returns { name, email_address }"""
    email_string = get_message_header(message, 'From')

    name, email_address = email.utils.parseaddr(email_string)

    return {
        'name': name,
        'emailAddress': email_address
    }


def get_email(email_string):
    _, email_address = email.utils.parseaddr(email_string)

    return email_address


def b64_to_plain_text(b64_text):
    return base64.urlsafe_b64decode(b64_text).decode('utf-8')


def get_parts(message):
    """Get parts from Gmail message object"""
    payload = message['payload']

    parts = payload.get('parts')

    if not parts:
        return None
        # import pprint
        # pprint.pprint(message)
        # raise ValueError("Couldn't get parts from message: {}".format(message))

    if parts[0].get('parts'):
        parts = parts[0].get('parts')

    return parts


def get_body_html(message):
    get_data_and_decode = lambda part: base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
    # get_data_and_decode = lambda part: b64_to_plain_text(part['body']['data'])


    parts = get_parts(message)


    if not parts:
        # plain text email
        return None

    message_html = next((get_data_and_decode(part) for part in parts if part['mimeType'] == 'text/html'), '')

    # TODO: Throw error if falsey?
    return message_html


def parse_email(parts):
    # TODO: Should we actually prefer plain_text?
    # Need to experiment to see how good Google's html2text is.
    # However, if it is primitive it could lead to lost inormation

    get_data_and_decode = lambda part: base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
    # get_data_and_decode = lambda part: b64_to_plain_text(part['body']['data'])

    message_html = next((get_data_and_decode(part) for part in parts if part['mimeType'] == 'text/html'), None)

    if message_html:
        return reply_parser.parse_email(whole_email_html=message_html)

    message_plain = next((get_data_and_decode(part) for part in parts if part['mimeType'] == 'text/plain'), None)

    if not message_plain:
        try:
            if parts[0].get('parts'):
                return parse_email(parts[0].get('parts'))
            else:
                raise ValueError('Error getting body from message, parts: {}'.format(parts))
        except:
            raise ValueError('Error getting body from message, parts: {}'.format(parts))

    return reply_parser.parse_email(whole_email_plain=message_plain)


def get_body_plain_text(parts):
    return parse_email(parts)['body']


def parse_message(message):
    """Parses body and returns constituent parts"""
    payload = message['payload']

    if payload.get('parts'):
        return parse_email(payload['parts'])
    else:
        # Plain text email
        whole_body_plain = b64_to_plain_text(payload['body']['data'])

        # print(type(whole_body_plain))
        # print(whole_body_plain)

        stripped_body = reply_parser.parse_email(whole_email_plain=whole_body_plain)

        # print(type(stripped_body))
        # print(stripped_body)

        return stripped_body


def get_message_plain_without_quoted_text(message):
    return parse_message(message)['body']


def get_from_email(message):
    """
    Get the email address the message was sent from
    """
    return get_email(get_message_header(message, 'From'))


def is_inbound(message, user_email_address):
    """
    Note: Aliases will break this

    TODO: Include keyword argument for aliases

    Arguments:
        message {[type]} -- [description]
        user {[type]} -- [description]
    """
    from_email_address = get_from_email(message)
    if from_email_address == user_email_address:
        return False

    # 'foster@draft-ai.com, Tiffany Gerald <tiffanygerald85@gmail.com>'
    # TODO: What if the name is "Gerald, Tiffany"?
    recipients_string = get_message_header(message, 'To')

    recipients = recipients_string.split(',')
    inbound = any(get_email(recipient) == user_email_address for recipient in recipients)

    # to_email_address = gmail_helper.get_from_email(message)
    # to_email_address = gmail_helper.get_email(gmail_helper.get_message_header(message, 'To'))
    # inbound = to_email_address == user_email_address


    # print('Is inbound: {}, from_email: {}, userEmailAddress: {}'.format(inbound, from_email_address, user_email_address))

    return inbound


def convert_message(message, timezone_string, user_email_address):
    """Convert message  to (plain_text, reference_date, inbound)"""

    plain_text = get_message_plain_without_quoted_text(message)
    reference_date = utils.epoch_timestamp_to_datetime(int(message['internalDate']) / 1000, timezone_string)
    inbound = is_inbound(message, user_email_address) # get_from_email(message) != user_email_address

    return (plain_text, reference_date, inbound)


def thread_to_drafting_input(thread, user_email_address, timezone_string):
    """
    Convert thread to list of emails in format [(plain_text, reference_date, inbound)]
    """

    list_of_messages = [convert_message(message, timezone_string, user_email_address) for message in thread['messages']]

    return list_of_messages


def watch_account_for_updates(user, set_delta=False):
    """
    set_delta should be True if an update to the user in the database is desired
    if we are simply ensuring the watches are still active this is not necessary

    Note: watch() will timeout after 7 days and needs to be called again

    Arguments:
        user {[type]} -- [description]

    Keyword Arguments:
        set_delta {bool} -- [description] (default: {False})
    """

    if user.get('expiration'):
        expiration_time = datetime.datetime.fromtimestamp(user['expiration'] / 1000)

        if expiration_time - datetime.datetime.now() > datetime.timedelta(days=1):
            # Only re-watch account if there is less than one day left
            return

    # Start watch() on email account
    gmail_service = get_service(user, 'gmail')

    watch_params = {
        'topicName': FULL_TOPIC_NAME,
        'labelIds': [
            'DRAFT',
            'SPAM',
        ],
        'labelFilterAction': 'exclude',
    }

    query = gmail_service.users().watch(userId='me', body=watch_params)
    response = query.execute()

    if set_delta:
        db_helper.update_history_delta(user, response['historyId'])

    db_helper.set_watch_expiration(user, int(response['expiration']))


def stop_watching_account(user):
    """Stop watching a user's account for changes"""
    gmail_service = get_service(user, 'gmail')

    query = gmail_service.users().stop(userId='me')
    query.execute()


###############################
# Helper functions for messages
###############################


WEBMAIL_DOMAINS_FILE = os.path.dirname(os.path.realpath(__file__)) + '/../data/webmail_domains.txt'


def get_webmail_domains():
    """Returns a set of webmail domains"""
    with open(WEBMAIL_DOMAINS_FILE) as webmail_domains_file:
        return set([webmail_domain for webmail_domain in webmail_domains_file.read().splitlines() if webmail_domain])


WEBMAIL_DOMAINS = get_webmail_domains()


# https://regex101.com/r/Ib9rOp/
IS_CALENDAR_INVITE_REGEX = re.compile(r'^(Invitation|(Tentatively )?Accepted|Declined|Updated:|Updated[ ]Invitation:)[ ].{2,}@.{2,}')
# https://regex101.com/r/JU4aEv/1
IS_SHARED_CALENDAR_NOTIFICATION_REGEX = re.compile(r'has shared a calendar with you$')


def is_calendar_invite(message):
    """Is message a calendar invitation or response"""
    subject = get_subject(message)

    return bool(IS_CALENDAR_INVITE_REGEX.match(subject))


def is_shared_calendar_notification(message):
    """Is email notification that someone has shared their calendar with you"""
    subject = get_subject(message)

    return bool(IS_SHARED_CALENDAR_NOTIFICATION_REGEX.match(subject))


def is_in_spam_folder(message):
    """Is message in spam folder"""

    return 'SPAM' in message.get('labelIds', [])


def is_draft(message):
    return 'DRAFT' in message.get('labelIds', [])


def is_noreply(message):
    """Determines if message was sent from a noreply@ or similar address"""

    from_email = get_from_email(message)

    if not from_email:
        # If we don't know what the from_email is then default False
        return False

    return bool(re.search(regexes.NOREPLY_EMAIL_ADDRESS, from_email))


def is_transaction_email(message):
    """
    Transactional email
        - If there is a link with the word 'unsubscribe' in it
    """

    body_html = get_body_html(message)
    if not body_html:
        return False

    soup = bs4.BeautifulSoup(body_html, 'lxml')

    for link in soup.find_all('a'):
        unsubscribe_in_text = 'unsubscribe' in link.text.lower()
        unsubscribe_in_href = 'unsubscribe' in link.get('href', '').lower()
        unsubscribe_in_text_before_link = False
        try:
            unsubscribe_in_text_before_link = 'unsubscribe' in str(link.previous).lower()[-30:]
        except RuntimeError:
            # bs4 sometimes gets a nasty recursion error
            logger.warning('Error parsing HTML - nonfatal')

        if unsubscribe_in_text or unsubscribe_in_href or unsubscribe_in_text_before_link:
            return True


    # TODO: This is too broad, some email signatures use tables for formatting as do some other programs (for example, forwarding pictures)
    # if soup.find_all('table') or soup.find_all('td'):
    #     return True


    return False


def get_subject(message):
    return get_message_header(message, 'Subject')


def is_bounced_email(message):
    """
    Detects bounced emails, uses the raw email if online else just the from email
    """

    from_email = get_from_email(message)

    if not from_email:
        return False

    subject = get_subject(message)

    if re.search(regexes.BOUNCE_EMAIL_ADDRESS, from_email) or re.search(regexes.BOUNCE_EMAIL_SUBJECT, subject):
        return True

    return False


def does_body_start_with_pipe(message):
    """
    Note: This is very heavy handed.
    Also, I suspect that only emails with tables in them start with pipe and therefore probably superfluous
    """

    body_html = get_body_html(message)

    if not body_html:
        return False

    try:
        plain_text = preprocess_text.H.handle(body_html)
    except:
        return False

    return plain_text.startswith('|')


# {
#   "id": string,
#   "threadId": string,
#   "labelIds": [
#     string
#   ],
#   "snippet": string,
#   "historyId": unsigned long,
#   "internalDate": long,
#   "payload": {
#     "partId": string,
#     "mimeType": string,
#     "filename": string,
#     "headers": [
#       {
#         "name": string,
#         "value": string
#       }
#     ],
#     "body": users.messages.attachments Resource,
#     "parts": [
#       (MessagePart)
#     ]
#   },
#   "sizeEstimate": integer,
#   "raw": bytes
# }


def convert_message_to_conversation_view(message, user):
    """
    {
        timestamp: Int,
        body: String,
        subject: String,
        inbound: Boolean,
        from: { name, emailAddress },
    }
    """

    # whole_email_html='', whole_email_plain='', from_email='', from_name='', to_name=''
    return {
        'timestamp': message['internalDate'],
        'subject': get_subject(message),
        'inbound': is_inbound(message, user['userEmailAddress']),
        'from': get_from_person(message),
        'body': parse_message(message),
    }


def convert_to_conversation_view(thread, user):
    """
    Convert thread for 'conversation view'

    [{
        timestamp: Int,
        body: String,
        subject: String,
        inbound: Boolean,
        from: { name, emailAddress },
    }]
    """
    return [convert_message_to_conversation_view(message, user) for message in thread['messages']]
