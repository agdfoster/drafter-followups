''' works out which emails are a user's emails based on...
more then x% of their emails coming from that address
TODO once this is working for multiple users, make this work for a list of users.'''
# import httplib2
# import base64
from pprint import pprint
import re

from get_messages import enrich_message, get_msgs_from_query, flatten
# import gmail_helper   # has some issues with relative import - libs perhaps ASK_MARTIN
# from gmail_quickstart import get_credentials
# from text_processing import reply_parser  # was causing import erros MARTIN_NOTE

# logger
from pprint import pformat
import os
from datetime import datetime
import logging
logging.getLogger('googleapiclient').setLevel(logging. CRITICAL + 10)
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

# database
from utils.db_vars import *

QUERY = 'from:me'
USER_ID = 'me'
NUM = 1000 # MAKE SURE THIS IS A BIG NUMBER UNLESS RUNNING TESTS
THRESHOLD = 0.05

def get_alias_list_db():
    '''get the aliases lists from db for checking against the user list'''
    
    return aliases_all_users

def get_user_list_from_db():
    '''get user list from db for checking against the alias list'''
    

def find_old_alias_lists(refresh_period, aliases_all_users):
    '''we want to refresh users' alias list regularly'''
    old_alias_ids = []
    for alias in aliases_all_users:
        age = datetime.now() - alias['date']
        age_days = age.total_seconds() / 60 / 60 / 24
        if age > refresh_period:
            old_alias_ids.append(alias['user_id'])
    return old_alias_ids


def get_list_of_users_to_build_aliases_for():
    ''' gets users list and aliases lists and returns a list of users
    that don't have aliases lists.'''


def build_alias_lists_for_missing_users():
    '''build_alias_lists_for_missing_users'''
    users = [user['email'] for user in db.user_creds.find({})]
    aliases_all_users = [alias['email'] for alias in db.alias_list.find({})]
    missing_users = [email for email in users if email not in aliases_all_users]
    logging.info('{} user/s have no alias list')
    for user in missing_users:
        get_aliases()


def rebuild_alias_lists_for_old_alias_lists():
    '''we want to refresh users' alias list regularly'''

def get_aliases(user_id='me'):
    ''' guesses the aliases for the user based on volume of 'sent' emails in query 'from:me' '''
    # first up, let's get a load of messages, 2000 say. also, enrich them.
    messages = get_msgs_from_query(service, 'me', 'from:me', NUM, start=0)
    logging.info('-----enriching %d messasges-----'%len(messages))
    # enrich em
    msgs = [enrich_message(message) for message in messages]
    # filter out msgs with no body, screw them.
    msgs = [msg for msg in msgs if msg['m_body']['plain'] or msg['m_body']['html']]

    #gmail includes all messages from threads where I've replied in the "from: me" query
    logging.debug('--------------------------------------------------------------------------')
    logging.debug('------------------------------LETS GET ALIASES----------------------------')
    logging.debug('--------------------------------------------------------------------------')
    # logging.debug(pformat(msgs, depth=3))
    # so we've got a bunch of msgs...
    # there's only ever one email in from so let's flatten the list of lists
    msgs_from = flatten([msg['h_from'] for msg in msgs])
    # logging.debug(pformat(msgs_from))

    # now let's make a nice pivot table of all those emails
    email_pivot = {}
    for item in msgs_from:
        email = item[0]
        email_pivot[email] = email_pivot.get(email, 0) + 1
    # convert to %, % is more useful than count()
    for k, v in email_pivot.items():
        

        email_pivot[k] = email_pivot[k] / round(len(msgs_from),3)
    logging.debug('number of possible aliases = %d'%len(email_pivot))
    logging.debug(pformat(email_pivot))

    # filter list to only the most frequent email addresses
    aliases = []
    for k, v in email_pivot.items():
        if v > THRESHOLD:
            aliases.append(k)
    logging.info('aliases = ' + str(aliases))
    # that's it - those your aliases
    return aliases

def put_alias_list_in_db(alias_list, fname, sname, email):
    ''' store alias lists for later user'''
    alias_object = {
        'alias_list': alias_list,
        'fname': fname,
        'sname': sname,
        'email': email,
        'user_id': email,
        'date':datetime.now()
    }
    # delete existing entries for this user
    num_existing_entries = len([item for item in db.alias_list.find({'user_id': email})])
    db.alias_list.delete_many({'user_id': email})
    logging.info('deleted {} existing alias entries for {}'.format(num_existing_entries, email))
    # put alias list in db
    db.alias_list.insert(alias_object)
    logging.info('inserted alias list for {}. Length = {}'.format(email, len(alias_object['alias_list'])))

if __name__ == '__main__':
    import get_gmail_service_obj
    service, fname, sname, email = get_gmail_service_obj.main()
    CLIENT_SECRET = os.environ['GOOGLE_OAUTH_CLIENT_SECRET']
    CLIENT_ID = os.environ['GOOGLE_OAUTH_CLIENT_ID']
    
    alias_list = get_aliases()
    put_alias_list_in_db(alias_list, fname, sname, email)