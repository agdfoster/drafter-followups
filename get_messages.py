''' my own set of gmail functions for getting emails from Gmail API 
get_msgs_from_query is the big one. Uses batches and relies on a gmail query.
'''

from gmail_quickstart import get_credentials
import httplib2
import base64
import email
import re
from googleapiclient.http import BatchHttpRequest
import time
from pprint import pprint
import math
service = get_credentials()

"""Get a list of Threads from the user's mailbox.
"""

from googleapiclient import errors

def list_threads_matching_query(service, user_id='me', query='', max_results=100):
    """ description:
        List all Threads of the user's mailbox matching the query.

        Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. The special value "me"
        can be used to indicate the authenticated user.
        query: String used to filter messages returned.
        Eg.- 'label:UNREAD' for unread messages only.

        Returns:
        List of threads that match the criteria of the query. Note that the returned
        list contains Thread IDs, you must use get with the appropriate
        ID to get the details for a Thread.
        """
    try:
        # get first page of results
        response = service.users().threads().list(userId=user_id, q=query).execute()
        threads = []
        if 'threads' in response:
            threads.extend(response['threads'])
        
        # each page is 100 results
        max_range = int(round(max_results/100-1, 0))
        if max_range > 1:
            for i in range(0, max_range):
                if 'nextPageToken' in response:
                    print('getting page %d'%i+1)
                    page_token = response['nextPageToken']
                    thread_ob = service.users().threads()
                    response = thread_ob.list(userId=user_id, q=query, pageToken=page_token).execute()
                    threads.extend(response['threads'])

        return threads
    except errors.HttpError as error:
        print('An error occurred: %s' % error)


def ListThreadsWithLabels(service, user_id, label_ids=[]):
    """List all Threads of the user's mailbox with label_ids applied.

    Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    label_ids: Only return Threads with these labelIds applied.

    Returns:
    List of threads that match the criteria of the query. Note that the returned
    list contains Thread IDs, you must use get with the appropriate
    ID to get the details for a Thread.
    """
    try:
        response = service.users().threads().list(userId=user_id,
                                            labelIds=label_ids).execute()
        threads = []
        if 'threads' in response:
            threads.extend(response['threads'])

        if 'nextPageToken' in response:
            page_token = response['nextPageToken']
            response = service.users().threads().list(userId=user_id,
                                                        labelIds=label_ids,
                                                        pageToken=page_token).execute()
            threads.extend(response['threads'])

        return threads
    except errors.HttpError as error:
        print('An error occurred: %s' % error)
#
def msg_ids_from_query(service, user_id, query='', max_results=100): #100=default to 1 pg of results
    """List all Messages of the user's mailbox matching the query.

        Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. The special value "me"
        can be used to indicate the authenticated user.
        query: String used to filter messages returned.
        Eg.- 'from:user@some_domain.com' for Messages from a particular sender.

        Returns:
        List of Messages that match the criteria of the query. Note that the
        returned list contains Message IDs, you must use get with the
        appropriate ID to get the details of a Message.
        """
    try:
        response = service.users().messages().list(userId=user_id, q=query).execute()
        print('getting IDs page 1')
        messages = []
        if 'messages' in response:
            messages.extend(response['messages'])
        # each page is 100 results - get results up to max_range
        xtra_pages = int(math.ceil((max_results-100)/100)-1) #math.ceil = roundup
        if max_results > 100 and xtra_pages+1 > 0:
            print('getting %d more pages'%int(xtra_pages+1))
            for i in range(2, xtra_pages+3):
                if 'nextPageToken' in response:
                    print('getting IDs page %d of %d'%(i, xtra_pages+2))
                    page_token = response['nextPageToken']
                    response = service.users().messages().list(userId=user_id, q=query, pageToken=page_token).execute()
                    messages.extend(response['messages'])
        return messages[:max_results]
    except errors.HttpError as error:
        print('An error occurred: %s' % error)
#

def get_message(service, user_id, msg_id):
    """Get a Message with given ID.

        Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. The special value "me"
        can be used to indicate the authenticated user.
        msg_id: The ID of the Message required.

        Returns:
        A Message.
        """
    try:
        message = service.users().messages().get(userId=user_id, id=msg_id).execute()
        # print( 'Message snippet: %s' % message['snippet'])
        return message
    except errors.HttpError as error:
        pprint( 'An error occurred: %s' % error)
#

def get_messages_batch(service, user_id, msg_ids):
    ''' get messages from ids as above - but using google's batch request
    it's much faster for getting lots of messages from IDs in one go.
    limit is 2000 at a time, just doesn't return more'''
    messages = []
    def gmail_callback(request_id, response, exception):
        ''' callback function for the below batch request
        appends messages returned to messages list
        when the batch request returns, even though it's all in one go
        it calls this function once for every message it returns'''
        if exception:
            raise exception
        # pprint(response, depth=3)
        messages.append(response)
        # what happens at > 2000 messages?
        # change flag to true when we have all the messages

    # run the Google API batch request
    batch = BatchHttpRequest()
    for msg_id in msg_ids:
        batch.add(service.users().messages().get(
            userId='me', id=msg_id['id']), callback=gmail_callback)
    batch.execute()
    
    # callbacks are Asynchronous so put a pause in that waits for it to finish
    timer = 0
    batch_request_complete = False
    while not batch_request_complete:
        batch_request_complete = len(messages) == len(msg_ids)
        time.sleep(0.5)
        # throw an error if it takes too long (30s)
        timer += 0.5
        we_have_been_waiting_too_long = timer == 30
        if we_have_been_waiting_too_long:
            raise Exception('Batch request did not complete in time')
    return messages

def get_msgs_from_query(service, user_id, query, max_results=50):
    '''wrapper function combining get ids from query
    and get messages batch. reccommended not to exceed 50 results'''
    print('getting message IDs')
    msg_ids = msg_ids_from_query(service, user_id, query, max_results)
    print('getting messages from IDs')
    messages = get_messages_batch(service, user_id, msg_ids)
    return messages


# def get_mime_message(service, user_id, msg_id):
#     '''get message and use it to create MIME message
#     THE MIME PARSER 'EMAIL' is hitting an error'''
#     message = service.users().messages().get(userId=user_id, id=msg_id, format='raw').execute()
#     print('Message snippet: %s' % message['snippet'])
#     msg_str = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))
#     # mime_msg = email.message_from_string(msg_str)
#     return msg_str
#

def get_to(message):
    ''' get just the to field of a message'''
    headers = message['payload']['headers']
    output = []
    for item in headers:
        # ran a test on 1000 emails and only found the below using vague set ['to','To','TO']
        # and if  any(x in item['name'] for x in to_variants) and not any(x in item['name'] for x in avoid):
        if  item['name'] == 'To' or item['name'] == 'Delivered-To':
            output.append(item['value'])
    return output
#
def flatten(list_of_lists):
    list_out = [item for sublist in list_of_lists for item in sublist]
    return list_out
#

def parse_out_email_address(email_header_item):
    people = email_header_item.split(",")
    # print('             ')
    # print('header = '+email_header_item)
    # print('people = %s'%str(people))
    output = []
    for person in people:
        # print('person = %s'%person)
        match = re.findall(r'<([^@]+?@[^@]+?)>', person)
        name = re.findall(r'([A-Z]\S+).*?<', person)
        if len(match) == 0:
            match = re.findall(r'([^\' ,<>]+@[^\' ,<>]+)', email_header_item)
        if len(match) == 0:
            print('- - - - - - - EMAIL ERROR - - - - - - - ')
        elif len(name) == 0:
            print('- - - - - - - NAME ERROR - - - - - - - ')
        elif len(match) > 1 or len(name) > 1:
            print('- - - - - - - MORE THAN ONE MATCH - - - - - - - ')
        elif not len(match) == 0 and not len(name) == 0:
            output.append([match[0], name[0]])
            print('output = %s and %s'%(str(name), str(match)))
    return output
#

if __name__ == '__main__':
    # START_TIME = time.time()

    def hitlist(results_max):
        # thread_ob = ListThreadsWithLabels(service,'me','INBOX')
        # threads = list_threads_matching_query(service, 'me', 'From:me',100)
        msg_ids = msg_ids_from_query(service, 'me', 'from: me', results_max)
        # print(msg_ids)
        # messages is now a list of ids and thread ids
        # get messages
        output = []
        for idx, message in enumerate(msg_ids):
            print('getting message %d'%(idx+1))
            m_id = message['id']
            message = get_message(service, 'me', m_id)
            to_header = get_to(message)
            people = parse_out_email_address(str(to_header))
            for person in people:
                output.append(person)
                with open("email_store.txt", "a") as myfile:
                    myfile.write(str(person)+'•\n')
        output = flatten(output)
        # out = set(output)
        print(output)
        print("finished")
            # pprint(to_field)

    def hitlist_batch(results_max):
        '''re-write the hit list function above using gmail batch'''
        # get message ids eg [{id: X, threadId: Y} , {id: X, threadId: Y}, etc ]
        msg_ids = msg_ids_from_query(service, 'me', 'from: me', results_max)
        # split list of id's into batches of 2000
        print('getting messages from %d ids'%len(msg_ids))
        messages = get_messages_batch(service, 'me', msg_ids)
        print('retrieved %d messages'%len(messages))
        output = []
        for idx, message in enumerate(messages):
            print('msg %d'%(idx+1))
            to_header = get_to(message)
            people = parse_out_email_address(str(to_header))
            for person in people:
                output.append(person)
                with open("email_store.txt", "a") as myfile:
                    myfile.write(str(person)+'•\n')
        output = flatten(output)
        # out = set(output)
        print(output)
        print("finished")

    # hitlist(100)
    # hitlist_batch(200)
    messages = get_msgs_from_query(service, 'me', 'from:me', 50)
    pprint(messages, depth = 5)
    
    # logging.info("--- %s seconds to execute ---", round((time.time() - START_TIME), 2))
