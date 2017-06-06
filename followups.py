''' find messages from user with no reply '''
import httplib2

import get_messages
# import gmail_helper   # has some issues with relative import - libs perhaps ASK_MARTIN
from pprint import pprint
from gmail_quickstart import get_credentials
SERVICE = get_credentials()

QUERY = 'from:me'
USER_ID = 'me'
NUM = 500

def main():

    # get messages from me from last 3 months
    # 1 get all message IDs
    msg_ids = get_messages.msg_ids_from_query(SERVICE, USER_ID, QUERY, NUM)
    print('----IDS----')
    pprint(msg_ids)
    # 2 get messages
    messages = get_messages.get_messages_batch(SERVICE, USER_ID, msg_ids)
    # print('----MESSAGES----')
    # pprint(messages, depth=2)

    # get message bodies
    # 1 get 64b body from paylod
    for message in messages:
        try:
            parts = message['payload']['parts']
        except:
            print('-----could not find parts------')
            pprint(message)
    

    # get_data_and_decode = lambda part: base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
    print('----64b----')
    # pprint(messages, depth=3)
    # [print(len(message)) for message in messages]
    # 

    # filter messages by those that don't include a question mark

    # get messages in same thread

    # filter messages by those with at least one reply

    # get later messages in same thread

    # get later messages from same person
        # identify who the message was *really* sent to

    # if message from same person / later message in thread - remove from list

    # list should now be those that need followups.

    # further classifiers...

if __name__ == '__main__':
    main()