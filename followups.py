''' find messages outoing from user with no reply and that we
classify as followups, this file does not the drafting of followups itself'''
import httplib2
import base64
from pprint import pprint
import re

from get_messages import enrich_message, get_msgs_from_query, flatten
# import gmail_helper   # has some issues with relative import - libs perhaps ASK_MARTIN
from gmail_quickstart import get_credentials
from utils import regex
# from text_processing import reply_parser  # was causing import erros MARTIN_NOTE

# logger
from pprint import pformat
import logging
logging.getLogger('googleapiclient').setLevel(logging. CRITICAL + 10)
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

SERVICE = get_credentials()
QUERY = 'from:me'
USER_ID = 'me'
ALIASES = ['foster@drafterhq.com', 'foster@drafter.email', 'foster@draft-ai.com']
NUM = 100


def main():
    # get messages from me from last 3 months
    # 1 get all message IDs
    messages = get_msgs_from_query(SERVICE, 'me', '', NUM, start=0)
    logging.info('-----enriching %d messasges-----'%len(messages))
    msgs = [enrich_message(message) for message in messages]
    msgs_no_body = [msg for msg in msgs if msg['m_body']['plain'] == None and msg['m_body']['html'] == None]
    logging.info(str(len(msgs_no_body)) + ' messages have no body')
    
    logging.debug('--------------------------------------------------------------------------')
    logging.debug('------------------------START OF FOLLOWUP FUNCTIONS-----------------------')
    logging.debug('--------------------------------------------------------------------------')
    
    # filter for messages sent by me
    # gmail includes all messages from threads where I've replied in the "from: me" query)'''
    # TODO alises are hard-coded for now
    logging.debug('for followups, number of msgs pre filtering = ' + str(len(msgs)))
    msgs_from_me = [msg for msg in msgs if msg['h_from'][0][0] in ALIASES]
    # check the above manually, are all these emails from me? NOTE: does not include agdfoster@gmail.com
    # for msg in msgs_from_me:
    #     logging.debug(msg['h_from'][0])

    # now filter messages by those that don't include a question mark
        # TODO ideally this would search for ?'s in questions incase one is included randomly
    msgs_w_q = []
    msgs_wo_q = []
    for msg in msgs_from_me:
        plain_stripped = msg['m_body']['plain_stripped']
        if '?' in plain_stripped:
            msg['question'] = regex.extract(plain_stripped, r'([^\n\r.!?]+\?)')
            msgs_w_q.append(msg)
        else:
            msgs_wo_q.append(msg)
    # manual check that it's detecting questions
    logging.debug('------ questions -------')
    for msg in msgs_w_q:
        logging.debug(msg['question'])
    logging.debug('number of emails w questions = %d out of %d'%(len(msgs_w_q), len(msgs_from_me)))

    # TODO get other messages in same threads

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