''' find messages outoing from user with no reply and that we
classify as followups (various conditions), then call the file that composes and drafts the email for us.
This is the Main function file for the app.'''
import httplib2
import base64
from pprint import pprint
import re
from pprint import pformat
from datetime import datetime, date, timedelta
import time
from itertools import groupby

# import google_auth
from get_messages import enrich_message, get_msgs_from_query, flatten
from get_messages2 import get_messages_from_dates_and_threads, define_search_period
# import gmail_helper   # has some issues with relative import - libs perhaps ASK_MARTIN
# from gmail_quickstart import get_credentials
from utils import regex
# database
from utils.db_vars import *
# from text_processing import reply_parser  # was causing import erros MARTIN_NOTE
import draft_followup
import get_gmail_service_obj
# logger
import logging
logging.getLogger('googleapiclient').setLevel(logging. CRITICAL + 10)
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)


# . env_vars.sh <<< TO RUN ENV VARS LOCALLY
# USER = {'googleRefreshToken': '1/tEQsqzKONt7h9BbTsG-x3pWu6XYBt-7UF1m_CxH7nc8'} # this is historic, not sure what for.
# SERVICE = google_auth.get_service(USER, 'gmail')
# QUERY = 'from:me'
USER_ID = 'me'
NUM = 1000 # limit number of threads to fetch
AFTER = define_search_period(3) # = '2017/06/10'
BEFORE = None
# db.msgs_without_to.drop()
# logging.info('logging db dropped')

def get_msgs_enrich_then_cache_em():
    # get messages from me from last 3 months
    # 1 get all message IDs
    # V1
    # messages = get_msgs_from_query(SERVICE, USER_ID, 'from:me', NUM, start=0) # VERSION 1
    # V2
    messages = get_messages_from_dates_and_threads(service, USER_ID, after=AFTER, before=BEFORE, max_results=NUM) # VERSION 2
    logging.info('-----enriching %d messasges-----'%len(messages))
    msgs = [enrich_message(message) for message in messages]
    msgs_no_body = [msg for msg in msgs if msg['m_body']['plain'] == None and msg['m_body']['html'] == None]
    logging.info(str(len(msgs_no_body)) + ' messages (of %d) have no body'%len(msgs))
    
    # cache the output
    db.cache.drop()
    for msg in msgs:
        db.cache.insert(msg)
    logging.info('msgs cached in db = %d'%len(msgs))
    return msgs



def get_msgs_from_cache():
    return db.cache.find({})



def get_aliases_from_db(user_id):
    ''' get users' aliases from db'''
    # get aliases from db TODO - ensure db has aliases (at least 'me ) and remove these hedges below
    try:
        alias_object = db.aliases_list.find({'user_id': user_id})
        aliases = [alias['alias_list'] for alias in alias_object]
    except:
        raise TypeError('FAILED TO GET ALIASES FROM DB')
    if len(aliases) > 0:
        logging.info('aliases = {}'.format(aliases))
    else:
        logging.info('no aliases found in db')
    return aliases

def guess_primary_to_email(msg, aliases):
        '''takes a list of aliases (emails) and on a single message, 
        guess who the conversation is directed at.
        this logic was more complex but is now simply, cycle through emails
        from the to field until you find one that is not blank'''
        # get the to header (list of email, name tuples)
        possible_answers = msg['h_to']
        if msg['direction'] == "INBOUND":
            return [None, None]
        for email, name in possible_answers:
            if email:
                if email not in aliases:
                    return [email, name]
                if (email in aliases):
                    logging.warning('WARNING - this inbound emails primary to is an alias')
                    msg['_message_type'] += ', primary to is alias'
        # otherwise return None obj
        return [None, None]

def num_business_days_between_timestamps(ts1, ts2):
    '''takes two unix timestamps and gives you number of BUSINESS DAYS
    (mon-fri) between two dates. rounds timestamps to dates'''
    # vars
    fromdate = datetime.fromtimestamp(ts1).date()
    todate = datetime.fromtimestamp(ts2).date()
    # calc num_days (code from https://stackoverflow.com/questions/3615375/python-count-days-ignoring-weekends)
    daygenerator = (fromdate + timedelta(x + 1) for x in range((todate - fromdate).days))
    num_days = sum(1 for day in daygenerator if day.weekday() < 5)
    return num_days

def enrich_2(msg, aliases):
    '''second enrich function adding more enrichments used by followup function
    >> '''
    # enrich msg direciton (inbound/outbound)
    print(msg['h_from'][0][0], aliases)
    if msg['h_from'][0][0] in aliases: # only ever one 'from' email
        msg['direction'] = 'OUTBOUND'
    else:
        msg['direction'] = 'INBOUND'

    # enrich: has question? what is question?
    # TODO - detect whether ? at end of scentence.
    if '?' in msg['m_body_stripped']:
        msg['question'] = regex.extract(msg['m_body_stripped'], r'([^\n\r.!?]+\?)')
        msg['has_question'] = True # this is kinda superfluous
    else:
        msg['question'] = None
        msg['has question'] = False # this is kinda superfluous
    
    # enrich the 'h_primary_to' is.
    # messages sometimes have multiple people in the to field
    # TODO this should be replaced by a thread property: Conversation With
    primary_to = guess_primary_to_email(msg, aliases)
    msg['h_to_email_primary'] = primary_to[0]
    msg['h_to_name_primary'] = primary_to[1]
    # LOG failures to get 'to' to db as these CANNOT DRAFT
    # TODO - this needs to log what user it is for.
    if primary_to[0] == None or primary_to[0] in aliases:
        db.msgs_without_to.drop # replace previous list
        # db.msgs_without_to.insert(msg)
    
    # fix date_sent - needs to be integer and /1000 to be standardised. Assumes all need to be /1000
    date_sent = int(msg['date_sent'])
    if date_sent > 1000000000000:
        date_sent = int(date_sent/1000)
    msg['date_sent'] = date_sent
    
    # enrich date_sent_readable
    msg['date_sent_r'] = datetime.fromtimestamp(date_sent).strftime('%d/%m/%Y %H:%M')

    # enrich date_age (age of message)
    msg['date_age'] = num_business_days_between_timestamps(date_sent, time.time()) #time.time() = unix time NOW.

    return msg


def get_most_recent_msgs_from_threads(msgs):
    '''builds a list of most recent msg_ids based on threads.
    i.e., checks each thread and returns the ids of the messages 
    that are the most recent msg. also returns the threads object 
    for further use.'''
    # get list of thread ids
    thread_ids = [msg['id_thread'] for msg in msgs]
    thread_ids = set(thread_ids)
    logging.info('built thread_ids object with {} threads'.format(len(thread_ids)))

    # build threads object and list of most recent msg_ids
    # can't enrich status of 'most recent' as it is time bound and would make storage unreliable later
    # by building a list of most recent msg ids we can do a simple 'is in' check to see if most recent msg.
    # db.threads.drop()
    threads = []
    most_recent_msg_ids = []
    for thread_id in thread_ids:
        thread = [msg for msg in msgs if msg['id_thread'] == thread_id]
        threads.append(threads)
        
        # manual check - add threads to db for manual checks (check is most recent)
        # note - turn on the collection drop above as well.
        # db.threads.insert(thread)
        
        # get most recent message in thread
        most_recent_msg = max(thread, key=lambda msg: msg['date_sent'])
        most_recent_msg_ids.append(most_recent_msg['id_message'])
    
    return most_recent_msg_ids, threads


def is_calendar_invite(msg):
    pass

def is_unsubscribe_email(msg):
    pass

# check for later messages in other threads
def more_recent_msg_in_other_thread(msg, msgs):
    ''' checks a list of msgs to see if there is a more recent
    message from or to the same email address
    where email is the TARGET (to) of the msg passed in
    returns a list of more recent msgs if true and None if false
    TODO: this should diclude auto-emails'''
    target_email = msg['h_to_email_primary']
    date_sent = msg['date_sent']
    more_recent_msgs = []
    for msg in msgs:
        # ignore future messages that are cal invites, html-only, forwards, drafts...
        if any(x in msg['_message_type'] for x in ['calendar_invite', 'html_only', 'forward', 'draft']):
            # look for LATER messages with target email in primary_to or from
            if target_email in [msg['h_to_email_primary'], msg['h_from']] and date_sent < msg['date_sent']:
                more_recent_msgs.append(msg)
    if len(more_recent_msgs) == 0:
        return None
    else: 
        return more_recent_msgs


def msgs_req_followups(msgs, most_recent_msg_ids_from_threads, theshold_days):
    ''' returns msgs that req followups for a given threshold
    the threshold is a number of days with no response'''
    msgs_fom_me_w_q_and_most_recent = [
        msg for msg in msgs 
        if msg['direction'] == 'OUTBOUND' 
        and msg['question'] 
        and msg['id_message'] in most_recent_msg_ids_from_threads # in threads
        and not more_recent_msg_in_other_thread(msg, msgs) # across threads
        and msg['date_age'] >= theshold_days
        ]
    return msgs_fom_me_w_q_and_most_recent

def main(msgs):
    ''' run the logic to work out which messages to draft followups for
    then DRAFT the response for those messages'''
    # input vars
    threshold_days = 0
    # convert from cursor object to list
    msgs = [msg for msg in msgs]

    logging.info('--------------------------------------------------------------------------')
    logging.info('------------------------START OF FOLLOWUP FUNCTIONS-----------------------')
    logging.info('--------------------------------------------------------------------------')

    # get aliases
    logging.info('getting aliases...')
    aliases = get_aliases_from_db(USER_ID)

    # run enrich_2 on all msgs
    logging.info('starting enrichment 2')
    for msg in msgs:
        enrich_2(msg, aliases)

    # some info logs on message filters
    num_msgs_from_me = len(list([msg for msg in msgs if msg['direction'] == 'OUTBOUND']))
    num_msgs_fom_me_w_questions = len(list([msg for msg in msgs if msg['direction'] == 'OUTBOUND' and msg['question']]))
    num_msgs_missing_to = len(list([msg for msg in msgs if not msg['h_to_email_primary'] and msg['direction'] == 'OUTBOUND']))
    logging.info('number of messages outbound = %d of %d'%(num_msgs_from_me, len(msgs)))
    logging.info('number of messages outbound w questions = %d out of %d'%(num_msgs_fom_me_w_questions, num_msgs_from_me))
    logging.info('number of messages outbound missing primary to = %d out of %d'%(num_msgs_missing_to, num_msgs_from_me))

    # TODO for now assume that primary to is good enough. You're probably going to reply to the last person you sent the message to.

    # at this point we should be at the end game - we now (and only now) filter down to the messages to draft for.

    # check each thread and return a list of messages that are 'the most recent'. 
    # As time bound, do not enrich this to allow for storage / caching.
    most_recent_msg_ids, threads = get_most_recent_msgs_from_threads(msgs)
    logging.info('Built list of most recent msg ids. Found {} for {} threads.'.format(format(len(most_recent_msg_ids)), len(threads)))

    # log progress
    num_msgs_fom_me_w_q_and_most_recent = len(list([msg for msg in msgs if msg['direction'] == 'OUTBOUND' and msg['question'] and msg['id_message'] in most_recent_msg_ids]))
    logging.info('number of mesaged outbound w questions and is most recent = {} out of {}'.format(num_msgs_fom_me_w_q_and_most_recent, num_msgs_from_me))

    msgs_to_draft_for = msgs_req_followups(msgs, most_recent_msg_ids, threshold_days)
    
    logging.info('number of mesaged outbound w questions and is most recent across threads = {} out of {}'.format(len(msgs_to_draft_for), num_msgs_from_me))
    if len(msgs_to_draft_for) == 0:
        raise TypeError('NO MESSAGES TO DRAFT FOR FOUND, CHECK YOUVE DELETED THE TEST DRAFTS')
    logging.info('--------------------------------------------------------------------------')
    logging.info('---------------------------MESSAGES TO DRAFT FOR--------------------------')
    logging.info('--------------------------------------------------------------------------')
    logging.info(pformat(msgs_to_draft_for, depth=2))
    # further classifiers...

    return msgs_to_draft_for

def draft_followups_wrapper(msgs_to_draft_for, fname, sname, user_id):
    # Draft message! different function, make sure you keep people in cc and say hello to the right person.
    logging.info('asking gmail to draft {} messages'.format(len(msgs_to_draft_for)))
    num_drafts_successful = 0
    for msg in msgs_to_draft_for:
        user_email = user_id
        msg_to_reply_to = msg

        # run the file that drafts emails
        draft_followup.main(service, user_email, msg_to_reply_to, fname, sname)

        num_drafts_successful += 1
    logging.info('{} of {} drafts drafted'.format(num_drafts_successful, len(msgs_to_draft_for)))

if __name__ == '__main__':
    start_timer = datetime.now()
    # service and vars
    service, fname, sname, email = get_gmail_service_obj.main()
    
    # get messages from cache or get msgs from API (and repopulate cache)
    # msgs = get_msgs_from_cache()
    msgs = get_msgs_enrich_then_cache_em()
    
    # execute logic
    msgs_to_draft_for = main(msgs)

    # draft followups
    draft_followups_wrapper(msgs_to_draft_for, fname, sname, email)

    execution_time = datetime.now() - start_timer
    logging.info('finished! Executed in {}s'.format(execution_time.total_seconds()))
