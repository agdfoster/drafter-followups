''' works out which emails are a user's emails based on...
more then x% of their emails coming from that address'''
# import httplib2
# import base64
from pprint import pprint
import re

from get_messages import enrich_message, get_msgs_from_query, flatten
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
NUM = 2000
THRESHOLD = 0.05

def get_aliases(user_id='me'):
    ''' guesses the aliases for the user based on volume of 'sent' emails in query 'from:me' '''
    # first up, let's get a load of messages, 2000 say. also, enrich them.
    messages = get_msgs_from_query(SERVICE, 'me', 'from:me', NUM, start=0)
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

if __name__ == '__main__':
    get_aliases()