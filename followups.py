''' find messages outoing from user with no reply and that we
classify as followups, this file does not the drafting of followups itself'''
import httplib2
import base64
from pprint import pprint
import re

from get_messages import msg_ids_from_query, get_messages_batch
from get_messages import enrich_message
# import gmail_helper   # has some issues with relative import - libs perhaps ASK_MARTIN
from gmail_quickstart import get_credentials
# from text_processing import reply_parser  # was causing import erros MARTIN_NOTE

SERVICE = get_credentials()
QUERY = 'from:me'
USER_ID = 'me'
NUM = 5


def parse_message(message):
    """ Martin function: Parses body and returns constituent parts"""
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

def parse_email(parts):
    # TODO: Should we actually prefer plain_text?
    get_data_and_decode = lambda part: base64.urlsafe_b64decode(
        part['body']['data']).decode('utf-8')
    message_html = next((get_data_and_decode(part) for part in parts if part['mimeType'] == 'text/html'), None)
    message_plain = next((get_data_and_decode(part) for part in parts if part['mimeType'] == 'text/plain'), None)
    
    # try various things to make it work
    if message_html:
        return reply_parser.parse_email(whole_email_html=message_html)
    if not message_plain:
        try:
            if parts[0].get('parts'):
                return parse_email(parts[0].get('parts'))
            else:
                raise ValueError('Error getting body from message, parts: {}'.format(parts))
        except:
            raise ValueError('Error getting body from message, parts: {}'.format(parts))

    return reply_parser.parse_email(whole_email_plain=message_plain)


def main():
    # get messages from me from last 3 months
    # 1 get all message IDs
    msg_ids = msg_ids_from_query(SERVICE, USER_ID, QUERY, NUM)
    print('----IDS----')
    pprint(msg_ids)
    # 2 get messages
    messages = get_messages_batch(SERVICE, USER_ID, msg_ids)
    print('----MESSAGES----')
    pprint(messages, depth=2)
    
    # build nice message bodies into message objects
    msgs = [enrich_message(message) for message in messages]
        
    print('-----ENRICHED MESSAGES-----')
    
    
    msgs = [msg for msg in msgs if msg]
    for msg in msgs:
        # replace paragraphs with •••
        msg['body_plain'] = re.sub(r'(\r\n){2,}',' ••• ',msg['body_plain'])
        # replace remaining non para line breaks with •
        msg['body_plain'] = re.sub(r'(\r\n)',' • ',msg['body_plain'])
    pprint(msgs, depth=4)
    # print(msgs[4]['body_plain'])
    
    # filter for messages sent by me
    '''(gmail includes all messages from threads where I've replied in the "from: me" query)'''
    # 1 using the user email
    # 2 write function for detecting user's aliases

    # filter messages by those that don't include a question mark

    # get messages in same thread

    # filter messages by those with at least one reply

    # get later messages in same thread

    # get later messages from same person
        # identify who the message was *really* sent to

    # if message from same person / later message in thread - remove from list

    # list should now be those that need followups.

    # Draft message! different function, make sure you keep people in cc and say hello to the right person.

    # further classifiers...

if __name__ == '__main__':
    main()