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
import logging
from _log_config import logg_init
logg_init()

SERVICE = get_credentials()
QUERY = 'from:me'
USER_ID = 'me'
NUM = 5


def main():
    # get messages from me from last 3 months
    # 1 get all message IDs
    messages = get_msgs_from_query(SERVICE, 'me', 'from:me', 100, start=0)
    logging.info('-----enriching %d messasges-----'%len(messages))
    msgs = [enrich_message(message) for message in messages]
    
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