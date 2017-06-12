''' find messages outoing from user with no reply and that we
classify as followups, this file does not the drafting of followups itself'''
import httplib2
import base64
from pprint import pprint
import re

from get_messages import enrich_message, get_msgs_from_query
# import gmail_helper   # has some issues with relative import - libs perhaps ASK_MARTIN
from gmail_quickstart import get_credentials
# from text_processing import reply_parser  # was causing import erros MARTIN_NOTE

# logger
from pprint import pformat
import logging
logging.getLogger('googleapiclient').setLevel(logging. CRITICAL + 10)
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

SERVICE = get_credentials()
QUERY = 'from:me'
USER_ID = 'me'
NUM = 100


def main():
    # get messages from me from last 3 months
    # 1 get all message IDs
    messages = get_msgs_from_query(SERVICE, 'me', 'from:me', NUM, start=0)
    logging.info('-----enriching %d messasges-----'%len(messages))
    msgs = [enrich_message(message) for message in messages]
    msgs_no_body = [msg for msg in msgs if msg['m_body']['plain'] == None and msg['m_body']['html'] == None]
    logging.info(str(len(msgs_no_body)) + ' messages have no body')

    # filter for messages sent by me
    '''(gmail includes all messages from threads where I've replied in the "from: me" query)'''
    # for 
    # 1 using the user email
    logging.debug('--------------------------------------------------------------------------')
    logging.debug('------------------------START OF FOLLOWUP FUNCTIONS-----------------------')
    logging.debug('--------------------------------------------------------------------------')
    # logging.debug(pformat(msgs, depth=3))
    logging.debug('for followups, number of msgs pre filtering = ' + str(len(msgs)))
    msgs_from = [msg['h_from'] for msg in msgs]
    logging.debug(pformat(msgs_from))

    # 2 TODO write function for detecting user's aliases

    # filter messages by those that don't include a question mark

    # get messages in same thread

    # now batch that

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