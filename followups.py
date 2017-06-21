''' find messages outoing from user with no reply and that we
classify as followups, this file does not the drafting of followups itself'''
import httplib2
import base64
from pprint import pprint
import re
from pprint import pformat

import google_auth
from get_messages import enrich_message, get_msgs_from_query, flatten
from get_messages2 import get_messages_from_dates_and_threads
# import gmail_helper   # has some issues with relative import - libs perhaps ASK_MARTIN
# from gmail_quickstart import get_credentials
from utils import regex
from utils.db_vars import *
# from text_processing import reply_parser  # was causing import erros MARTIN_NOTE

# logger

import logging
logging.getLogger('googleapiclient').setLevel(logging. CRITICAL + 10)
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

USER = {
    'googleRefreshToken': '1/tEQsqzKONt7h9BbTsG-x3pWu6XYBt-7UF1m_CxH7nc8'
}
SERVICE = google_auth.get_service(USER, 'gmail')
QUERY = 'from:me'
USER_ID = 'me'
ALIASES = ['foster@drafterhq.com', 'foster@drafter.email', 'foster@draft-ai.com']
NUM = 200
AFTER = '2017/06/10'
BEFORE = None
db.msgs_without_to.drop()
logging.info('logging db dropped')

def main():
    # get messages from me from last 3 months
    # 1 get all message IDs
    # V1
    # messages = get_msgs_from_query(SERVICE, USER_ID, 'from:me', NUM, start=0) # VERSION 1
    # V2
    messages = get_messages_from_dates_and_threads(SERVICE, USER_ID, after=AFTER, before=BEFORE) # VERSION 2
    # TODO build a get_msgs_in_threads_from_query - extends to all msgs in threads.
    logging.info('-----enriching %d messasges-----'%len(messages))
    msgs = [enrich_message(message) for message in messages]
    msgs_no_body = [msg for msg in msgs if msg['m_body']['plain'] == None and msg['m_body']['html'] == None]
    logging.info(str(len(msgs_no_body)) + ' messages (of %d) have no body'%NUM)
    
    logging.debug('--------------------------------------------------------------------------')
    logging.debug('------------------------START OF FOLLOWUP FUNCTIONS-----------------------')
    logging.debug('--------------------------------------------------------------------------')
    
    # filter for messages sent by me
    # gmail includes all messages from threads where I've replied in the "from: me" query)'''
    # TODO alises are hard-coded for now
    msgs_from_me = [msg for msg in msgs if msg['h_from'][0][0] in ALIASES]
    logging.debug('for followups, %d x msgs pre filtering vs., %d from me'%(len(msgs), len(msgs_from_me)))
    # check the above manually, are all these emails from me? NOTE: does not include agdfoster@gmail.com
    # for msg in msgs_from_me:
    #     logging.debug(msg['h_from'][0])

    # now filter messages by those that don't include a question mark
        # TODO ideally this would search for ?'s in questions incase one is included randomly
    msgs_w_q = []
    msgs_wo_q = []
    for msg in msgs_from_me:
        plain_stripped = msg['m_body_stripped']
        if '?' in plain_stripped:
            msg['question'] = regex.extract(plain_stripped, r'([^\n\r.!?]+\?)')
            msgs_w_q.append(msg)
        else:
            msgs_wo_q.append(msg)
    # manual check that it's detecting questions
    #   logging.debug('------ questions -------')
    # for msg in msgs_w_q:
    #     logging.debug(msg['question'])
    logging.debug('number of emails w questions = %d out of %d'%(len(msgs_w_q), len(msgs_from_me)))

    # TODO get other messages in same threads
    # we don't need to do this if we're confident we have messages going back far enough.
    # only really important for detecting F2 F3 etc
    # TODO now batch that
    # TODO Filter out mail merge emails

    # who is message sent to? (conversation with)
    def guess_primary_to_email(msg):
        ''' on a single message, guess who the conversation is directed at.
        this logic was more complex but is now simply, cycle through emails
        from the to field until you find one that is not blank'''
        # get the to header (list of email, name tuples)
        possible_answers = msg['h_to']
        backup_email = backup_name = None
        for email, name in possible_answers:
            if email and email not in ALIASES:
                return [email, name]
            if email and email in ALIASES:
                backup_email = email
                backup_name = name
        # if haven't returned yet, it's either None or an alias
        if backup_email:
            return [backup_email, backup_name]
        # otherwise,
        return [None, None]
#
    error_list = []
    for msg in msgs_w_q:
        primary_to = guess_primary_to_email(msg)
        # TODO msg['conv_with'] = 'todo'
        msg['h_to_email_primary'] = primary_to[0]
        msg['h_to_name_primary'] = primary_to[1]
        # logging.debug(msg['h_to_email_primary'])
        # LOG failures to get 'to' to db as these CANNOT DRAFT
        if primary_to[0] == None or primary_to[0] in ALIASES:
            error_list.append(msg)
            db.msgs_without_to.insert(msg)
        

    # get later messages from same person
    
    # if message from same person / later message in thread - remove from list

    # list should now be those that need followups.

    # Draft message! different function, make sure you keep people in cc and say hello to the right person.

    # further classifiers...

if __name__ == '__main__':
    main()