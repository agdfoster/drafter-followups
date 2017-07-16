# coding=<utf-8>
''' gets gmail messages and re-standardises the messages.
my own set of gmail functions for getting emails from Gmail API.
get_msgs_from_query is the big one. Uses batches and relies on a gmail query.

'''


import base64
import email
import re
import time
from pprint import pprint,pformat
import math
import logging

import httplib2
from html2text import html2text
from googleapiclient.http import BatchHttpRequest
from googleapiclient import errors
from utils.deep_get import deep_get, deep_get_all
from text_processing.reply_parser import parse_email
# from gmail_quickstart import get_credentials
# import google_auth
from utils import regex

# USER = #{
#     'googleRefreshToken': '1/tEQsqzKONt7h9BbTsG-x3pWu6XYBt-7UF1m_CxH7nc8'
# }
# service = google_auth.get_service(USER, 'gmail')
logging.getLogger('googleapiclient').setLevel(logging. CRITICAL + 10)
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

# logger
# import logging
# import _log_config #import logg_init
# logg_init()



####################################################################################
# SEARCH GMAIL
# SEARCH GMAIL
####################################################################################

def list_threads_matching_query(service, user_id='me', query='', max_results=50):
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
                    logging.info('getting page %d'%i+1)
                    page_token = response['nextPageToken']
                    thread_ob = service.users().threads()
                    response = thread_ob.list(userId=user_id, q=query, pageToken=page_token).execute()
                    threads.extend(response['threads'])

        return threads
    except errors.HttpError as error:
        logging.info('An error occurred: %s' % error)


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
        logging.info('An error occurred: %s' % error)
#
def msg_ids_from_query(service, user_id, query='', max_results=100, after=None, before=None): #100=default to 1 pg of results
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

        'after' should be a timestamp or gmail date string, 
        query will return only messages AFTER that date.
        'before' is the same but will return messages BEFORE that date.

        NOTE - this function is now unstable with before/after
        as you do not know how many results you are going to get.
        TODO - think up some situations and get it to handle them.
        """
    # add dates to the query
    if after:
        if isinstance(after, int):
            # sometimes timestamp is 1000 times larger (miliseconds)
            if after > 1000000000000: after = after/1000
            # format date string in gmail query format
            after = datetime.fromtimestamp(after).strftime('%Y/%m/%d')
        if isinstance(after, str):
            query = 'after:' + after + ' ' + query
    if before:
        if isinstance(before, int):
            # sometimes timestamp is 1000 times larger (miliseconds)
            if before > 1000000000000: before = before/1000
            # format date string in gmail query format
            before = datetime.fromtimestamp(before).strftime('%Y/%m/%d')
        if isinstance(before, str):
            query = 'before:' + before + ' ' + query
    logging.info('searching using query = %s'%query)
    try:
        response = service.users().messages().list(userId=user_id, q=query).execute()
        logging.info('getting message IDs from gmail page 1')
        messages = []
        if 'messages' in response:
            messages.extend(response['messages'])
        # each page is 100 results - get results up to max_range
        xtra_pages = int(math.ceil((max_results-100)/100)-1) #math.ceil = roundup
        if max_results > 100 and xtra_pages+1 > 0:
            logging.info('getting %d more pages'%int(xtra_pages+1))
            for i in range(2, xtra_pages+3):
                if 'nextPageToken' in response:
                    logging.info('getting message IDs from gmail %d of %d'%(i, xtra_pages+2))
                    page_token = response['nextPageToken']
                    response = service.users().messages().list(userId=user_id, q=query, pageToken=page_token).execute()
                    messages.extend(response['messages'])
        return messages[:max_results]
    except errors.HttpError as error:
        logging.info('An error occurred: %s' % error)
#

####################################################################################
# RETRIEVE MESSAGES
# RETRIEVE MESSAGES
####################################################################################

def get_single_message(service, user_id, msg_id):
    """Get a Message with given ID.
    Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. or the special value "me"
    Returns a Message."""
    try:
        message = service.users().messages().get(userId=user_id, id=msg_id).execute()
        # logging.info( 'Message snippet: %s' % message['snippet'])
        return message
    except errors.HttpError as error:
        plogging.info( 'An error occurred: %s' % error)
#

def get_messages_batch(service, user_id, msg_ids):
    ''' get messages from ids as above - but using google's batch request
    it's much faster for getting lots of messages from IDs in one go.
    limit is 2000 at a time, just doesn't return more'''
    # Callback function (for use in a sec)
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
    timeout = 30 #secs
    batch_request_complete = False
    while not batch_request_complete:
        batch_request_complete = len(messages) == len(msg_ids)
        time.sleep(0.5)
        # throw an error if it takes too long (30s)
        timer += 0.5
        we_have_been_waiting_too_long = timer == timeout
        if we_have_been_waiting_too_long:
            raise Exception('Alex: Batch request did not complete in %ds'%timeout)
    return messages

def get_messages_batch_throttled(service, user_id, msg_ids, start=0):
    ''' chop msg_ids into lists of lists of length n
    and calls get_message_batch every x seconds to throttle it
    and avoid hitting gmail api rate limits.
    get_message_batch handles waiting for callbacks so this function...
    only proceeds a step once it has the last functions callback.
    > note that start point is not an offset... 
    ... 2000 results starting at 1999 returns 1 result'''
    # Tested on 2000 - 
    # Tested on 10000 -
    # tested on 100000 - 
    n = 50 # recommended figure from google for all batch APIs
    sleep = 0.2 # setting to 0 works but unsafe incase of extra fast callbacks. only 10% speed benefits beyond 0.2s in tests
    # chunk up message id list into lists of lists [[idslist],[idslist]]
    msg_id_chunks = [msg_ids[i:i + n] for i in range(start, len(msg_ids), n)]
    # get all messages for those chunks in throttled fashion
    all_messages_chunks = []
    for idx, msg_id_chunk in enumerate(msg_id_chunks):
        message_chunk = get_messages_batch(service, user_id, msg_id_chunk)
        time.sleep(sleep)
        all_messages_chunks.append(message_chunk)
        logging.info('----- GETTING MESSAGES FROM GMAIL %d of %d -----'%((idx+1)*50, 50*len(msg_id_chunks)))
        # pprint(message_chunk, depth=2)
    logging.info('----- FINISHED GETTING CHUNKED MESSAGES -----')
    # all_message_chunks is now a list of lists - flatten it into list.
    messages = flatten(all_messages_chunks)
    # return list of message objects
    return messages


def get_msgs_from_query(service, user_id, query, max_results=50, start=0):
    '''wrapper function combining get ids from query
    and get messages batch. reccommended not to exceed 50 results
    > note that start point is not an offset... 
    ... 2000 results starting at 1999 returns 1 result'''
    # get message IDs
    logging.info('-----getting message IDs-----')
    msg_ids = msg_ids_from_query(service, user_id, query, max_results)
    # get messages (using list of IDs)
    logging.info('-----getting messages from IDs-----')
    messages = get_messages_batch_throttled(service, user_id, msg_ids, start)
    logging.info('-----got %d messages-----'%len(messages))
    return messages

####################################################################################
# NON BODY ENRICHMENT FUNCTIONS
# NON BODY ENRICHMENT FUNCTIONS
####################################################################################

def get_to(headers):
    ''' get just the to field of a message
    Note: 'Delivered to' originally I thought was valuable but it
    looks like just 'To' is all you need'''
    # headers = message['payload']['headers']
    # for item in headers:
        # ran a test on 1000 emails and only found the below using vague set ['to','To','TO']
        # if item['name'] == 'Delivered-To': # removed 'In-Reply-To'
        #     if regex.match(item['value'], r'@'): # has an email in it
        #         return item
    # used to be 'if item in' but split it so that it always takes delivered to if it finds it
    for item in headers:
        if item['name'] == 'To':
            if regex.match(item['value'], r'@'): # has an email in it
                return item
#

def get_from(headers):
    ''' get just the to field of a message'''
    # headers = deep_get_all[message, 'headers']
    for item in headers:
        # ran a test on 1000 emails and only found the below using vague set ['to','To','TO']
        if  item['name'] in ['From'] or 'From' in item['name']:
            return item
#
def get_subject(message):
    return get_message_header_item(message, 'Subject')

def get_message_header_item(message, header_name):
    ''' martin's generic header finder function'''
    headers = message['payload']['headers']
    # import pprint
    # pprint.pprint(headers)

    try:
        value = next(header['value'] for header in headers if header['name'] == header_name)
    except StopIteration:
        # most messages don't have cc so don't log for that. 
        if header_name != 'Cc':
            logging.warning('Could not find header "%s" in message "%s"', header_name, message['id'])
        return ''

    return value

def get_headers(message):
    '''TODO - builds a header object that works for all emails'''
    pass

def flatten(list_of_lists):
    list_out = [item for sublist in list_of_lists for item in sublist]
    return list_out
#

def parse_email_and_name(email_header_item, msg_id):
    ''' extract email and name from an email header item.
    NOTE - takes email header item (string) NOT whole header'''
    # checks
    if not email_header_item:
        return [[None, None]]
    # logging.info('email_header_item '+str(item_value))
    people = email_header_item['value'].split(",")
    # logging.info('people '+str(people))
    clean_header_item = []
    for person in people:
        person = str(person)
        # logging.info('person = %s'%person)
        email = re.findall(r'<([^@]+?@[^@]+?)>', person)
        name = re.findall(r'([A-Za-z][^ „‚“‟‘‛"()”’"❛❜❝❞❮❯<>〝〞＂]+).*?<', person)
        # logging.info('email = %s'%email)
        # backup parse method
        if len(email) == 0:
            email = re.findall(r'([^\' ,<>]+@[^\' ,<>]+)', person)
        # if no name in header item, set it to [None]
        if len(name) == 0:
            name = [None]
        # no email found - non breaking error
        if len(email) == 0:
            logging.debug('- - - - - - - failed to extract email for %s - - - - - - - '%msg_id)
            clean_header_item.append([None, None])
        # two emails in one header item - non breaking error, something is wrong.
        elif len(email) > 1 or len(name) > 1:
            logging.critical('- - - - - - - CRITICAL ERROR MORE THAN ONE EMAIL IN HEADER ITEM for  %s- - - - - - - '%msg_id)
            clean_header_item.append([None, None])
        # return so long as neither of the above happened
        else:
            clean_header_item.append([email[0], name[0]])
    return clean_header_item
#

####################################################################################
# BODY EXTRACTION ENRICHMENT FUNCTIONS
# BODY EXTRACTION ENRICHMENT FUNCTIONS
####################################################################################

def get_parts(message):
    """ Get parts from Gmail message object
    parts are the various different ways the body is formatted
    generally sent in both HTML and plain_text """
    # payload = message['payload']
    # parts = payload.get('parts')
    # pprint(payload)
    parts = flatten(deep_get_all(message, 'parts'))
    # if parts:
    #     if parts[0].get('parts'):
    #         parts = parts[0].get('parts')
    if not parts:
        # sometimes there is no 'parts' and the message is just in a body somewhere
        # I think this is having minimal effect
        body = deep_get(message, 'body')
        if body:
            logging.debug('COULD NOT FIND PART - FOUND BODY INSTEAD')
            # TODO THERE IS SOMETHING DODGE ABOUT THIS - returns HTML body ...
            # ...generally and pretty sure these messages are junk
            # now rebuild parts component
            parts = [{'body': body}]
        elif not body:
            logging.debug('failed to find parts')
            return None
        # import pprint
        # pprint.pprint(message)
        # raise ValueError("Couldn't get parts from message: {}".format(message))

    return parts

def get_body_using_mimetype(parts, mimetype='text/plain'):
    ''' returns a bs4 body out of a gmail's payload 'parts'
    requires mimetype e.g, text/plain or text/html
    DOES NOT TAKE LIST OF PARTS, just one email's parts list '''
    # return the body you are looking for if it can find it
    for body in parts:
        if body.get('mimeType') == mimetype:
            if not body.get('body',{}).get('data'):
                # logging.info(pformat(body))
                logging.info('ERROR - this mimetype body has no data...!')
                return None
            else:
                return body['body']['data']
    else: return None

# REPLACED BY ABOVE FUNCTION
# def get_body_plain_b64(parts):
#     ''' get's the b64 plain text out of a gmail's payload 'parts'
#     DOES NOT TAKE LIST OF PARTS, just one email's parts list '''
#     for body in parts:
#         if body['mimeType'] == 'text/plain':
#             return body['body']['data']
#         else: return None

# def get_body_html_b64(parts):
#     ''' get's the b64 *HTML* out of a gmail's payload 'parts'
#     DOES NOT TAKE LIST OF PARTS, just one email's parts list '''
#     for body in parts:
#         if body['mimeType'] == 'text/html':
#             return body['body']['data']
#         else: return None

def decode_b64(b64_string):
    ''' decodes a b64 string into an email,
    works for both html or plain text'''
    decoded = base64.urlsafe_b64decode(b64_string).decode('utf-8')
    return decoded

def get_message_body(message):
    ''' wrapper function for the above. Takes a gmail message object and returns body
    where body is both html and plain body decoded into english from b64.
    Will return None if object does not have both plain and HTML parts '''
    # 1 get parts from message payload
    # 'parts' is a list of body items within payload.
    parts = get_parts(message)
    # some messages are missing parts and just have the body
    # 2 filter out messages which don't have both plain text and html - fuck those guys.
    if not parts:
        logging.info('NO PARTS FOUND, EXCLUDED')
        body_plain = body_html = None
    # if len(parts) < 2:
    #     logging.info('MISSING EITHER PLAIN BODY OR HTML, EXCLUDED THIS ITEM')
    #     return None
    # if not parts[0] or not parts[1]:
    #     logging.info('EITHER PLAIN BODY OR HTML WAS NONETYPE, EXCLUDED THIS ITEM')
    #     return None
    # 3 get plain text and HTML and decode bs4
    body_plain_b64 = get_body_using_mimetype(parts, mimetype='text/plain')
    if body_plain_b64:
        body_plain = decode_b64(body_plain_b64)
    elif not body_plain_b64:
        logging.debug('failed to get body_plain_bs4 from mimetype')
        body_plain = None
    body_html_b64 = get_body_using_mimetype(parts, mimetype='text/html')
    if body_html_b64:
        body_html = decode_b64(body_html_b64)
    elif not body_html_b64:
        logging.debug('failed to get body_html_bs4 from mimetype')
        body_html = None
    # return body
    body = {
        'body_plain': body_plain,
        'body_html': body_html
        }
    return body

####################################################################################
# SPECIAL MESSAGE CATEGORISATION
# SPECIAL MESSAGE CATEGORISATION
####################################################################################

def categorize_message(message):
    '''returns a special category if the email is eg a cal invite'''
    msg_type = []

    parts = get_parts(message)
    if not parts:
        msg_type.append('no_parts')

    # Get Mimetypes
    if parts:
        mimes = [deep_get_all(part, 'mimeType') for part in parts]
        mimes = flatten(mimes)
        # print('mimetypes found = ' + str(mimes))

    # tag calendar invites
    for mime in mimes:
        if mime in ['text/calendar', 'application/ics']:
            msg_type += ', calendar_invite'

    # tag HTML ONLY in body
    body_plain = get_message_body(message)['body_plain']
    body_html = get_message_body(message)['body_html']
    if body_html and not body_html:
        msg_type += ', html_only'

    # tag forwarded message
    header_subject = get_subject(message)
    is_fwd = header_subject.startswith('Fwd:')
    if is_fwd:
        msg_type += ', forward'

    # tag draft messages
    labels = message.get('labelIds')
    if labels:
        if 'DRAFT' in labels:
            msg_type += ', draft'

    # if len(msg_type) == 0: msg_type = None
    if len(msg_type) > 1: msg_type = set(msg_type)
    return ', '.join(msg_type)

####################################################################################
# QUOTED TEXT EXTRACTION AND BASIC MESSAGE SEGMENTATION
# QUOTED TEXT EXTRACTION AND BASIC MESSAGE SEGMENTATION
####################################################################################

def segment_message(msg):
    whole_email_html = msg['m_body_html']['spacer']
    whole_email_plain = msg['m_body_plain']['spacer']
    from_email = msg['h_from'][0][0]
    from_name = msg['h_from'][0][1]
    to_name = msg['h_to'][0][1]
    
    return parsed_email


####################################################################################
# ENRICHMENT WRAPPER
# ENRICHMENT WRAPPER
####################################################################################

def enrich_message(message):
    '''wrapper for various parsing functions to put fields we want
    formatted nicely and in an easy to reach object location
    NOTE NOTE NOTE at this point the old object is moved down a level
    to hide it. all basic enrichment should ideally happen before this point
    msg replaces message to symbolise'''
    # categorize message
    message_type = categorize_message(message)
    # ids etc
    message_id = message.get('id')
    thread_id = message.get('threadId')
    snippet = message.get('snippet')
    labels = message.get('labelIds')
    # date, convert to int
    date_sent = int(message.get('internalDate'))
    # concatenate label list for easier reading (can do if in just as easily)
    if labels:
        labels = ', '.join(labels)
    
    # get item out of headers
    headers = flatten(deep_get_all(message, 'headers'))
    header_subject = get_subject(message)
    header_from = get_from(headers) # always there, always x1
    header_to = get_to(headers) # if missing, might be just a cc/bcc
    header_cc = get_message_header_item(message, 'Cc')
    # TODO: get_cc
    # TODO: get_bcc
    # parse header item string into structured obj
    header_from = parse_email_and_name(header_from, message_id)
    header_to = parse_email_and_name(header_to, message_id)
    header_to = list(filter(lambda x: x != None, header_to))
    # logging.info('-----ENRICHEMNT VALUES-----')
    # logging.info('from' + str(header_from))
    # logging.info('to' + str(header_to))
    
    # BODY WORK
    # extract and decode message body (just plain body for now)
    # for thread integrity it's important not to lose messages where possible
    body_plain = get_message_body(message)['body_plain']
    body_html = get_message_body(message)['body_html']
    if body_html:
        try:
            body_html2text = html2text(body_html)
        except:
            body_html2text = None
    else: body_html2text = None
    # some messages are just a blank message
    if not body_plain and snippet in ['', ' ', None]:
        body_plain = ''
    # if get message body fails...
    if not isinstance(body_plain, str) and not message_type:
        # there are legitimate reasons for no body eg: cal invite
        logging.debug('message type = ' + str(message_type))
        # otherwise - debug or ignore
        logging.debug('failed this payload: type: ' + str(body_plain))
        # logging.info(pformat(message))
    # create another message body which is more readable
    if isinstance(body_plain, str):
        # 1 replace paragraphs with '•••'
        body_plain_no_breaks = re.sub(r'(\r\n){2,}',' ••• ', body_plain)
        # 2 replace remaining non para line breaks with '•'
        body_plain_no_breaks = re.sub(r'(\r\n)',' • ', body_plain_no_breaks)
        # put structured values back into main messages object
    else:
        body_plain_no_breaks = 'No "body" to transform'
    # segment message, extract quoted text
    parsed_email = parse_email(body_html, body_plain, header_from[0][0], header_from[0][1], header_to[0][0])
    # buid return object
    msg = {
        'A': '---------------------------------------------------------------------------',
        'GMAIL': {'spacer': {'spacer': message}},
        'h_from': header_from,
        'h_to': header_to,
        'id_message': message_id,
        'id_thread': thread_id,
        'date_sent': date_sent,
        'm_snippet': snippet,
        'm_subject': header_subject,
        'm_body_stripped': parsed_email['body'],
        'm_body': {
                'html': body_html,
                'plain': body_plain,
                'html2text': body_html2text,
                'plain_no_breaks': body_plain_no_breaks,
                'greeting': parsed_email['greeting'],
                'signature': parsed_email['signature'],
                'signoff': parsed_email['signoff']
                },
        '_message_type': message_type
    }
    # few final touches
    # TODO add_conv_with(msg)
    return msg
#

####################################################################################
# DEV USE LOGIC
# DEV USE LOGIC
####################################################################################
if __name__ == '__main__':
    START_TIME = time.time()

    # def hitlist(results_max):
    #     ''' move this to own file, here for explanatory reasons for now'''
    #     # thread_ob = ListThreadsWithLabels(service,'me','INBOX')
    #     # threads = list_threads_matching_query(service, 'me', 'From:me',100)
    #     msg_ids = msg_ids_from_query(service, 'me', 'from: me', results_max)
    #     # logging.info(msg_ids)
    #     # messages is now a list of ids and thread ids
    #     # get messages
    #     output = []
    #     for idx, message in enumerate(msg_ids):
    #         logging.info('getting message %d'%(idx+1))
    #         m_id = message['id']
    #         message = get_single_message(service, 'me', m_id)
    #         to_header = get_to(message)
    #         people = parse_email_and_name(str(to_header))
    #         for person in people:
    #             output.append(person)
    #             with open("email_store.txt", "a") as myfile:
    #                 myfile.write(str(person)+'•\n')
    #     output = flatten(output)
    #     # out = set(output)
    #     logging.info(output)
    #     logging.info("finished")
    #         # pprint(to_field)

    # def hitlist_batch(results_max):
    #     ''' move this to own file, here for explanatory reasons for now
    #     re-write the hit list function above using gmail batch
    #     '''
    #     # get message ids eg [{id: X, threadId: Y} , {id: X, threadId: Y}, etc ]
    #     msg_ids = msg_ids_from_query(service, 'me', 'from: me', results_max)
    #     # split list of id's into batches of 2000
    #     logging.info('getting messages from %d ids'%len(msg_ids))
    #     messages = get_messages_batch(service, 'me', msg_ids)
    #     logging.info('retrieved %d messages'%len(messages))
    #     output = []
    #     for idx, message in enumerate(messages):
    #         logging.info('msg %d'%(idx+1))
    #         to_header = get_to(message)
    #         people = parse_email_and_name(str(to_header))
    #         for person in people:
    #             output.append(person)
    #             with open("email_store.txt", "a") as myfile:
    #                 myfile.write(str(person)+'•\n')
    #     output = flatten(output)
    #     # out = set(output)
    #     logging.info(output)
    #     logging.info("finished")

    # hitlist(100)
    # hitlist_batch(200)
    messages = get_msgs_from_query(service, 'me', 'from:me', 10, start=0)
    logging.info('-----enriching %d messasges-----'%len(messages))
    msgs = [enrich_message(message) for message in messages]

    for i, msg in enumerate(msgs):
        logging.info('----- msg %d stripped text-----'%i)
        logging.info(msg['m_body_stripped'])
    
    # INVESTIGATE MSGS with 0 length body_stripped
    msgs_failed_strip = [
        msg for msg in msgs 
        if len(msg['m_body_stripped']) < 10
        and not msg['_message_type'] == 'calendar_invite'
    ]
    # logging.info(pformat(msgs_failed_strip, depth=4))


    # INVESTIGATE MSGS WITH NO BODY
    msgs_no_body = [msg for msg in msgs if msg['m_body']['plain'] == None and msg['m_body']['html'] == None]
    # for msg in msgs_no_body:
    #     print('-----------------------NO BODY EMAILS-------------------------------')
    #     pprint(msg['GMAIL']['spacer']['spacer']['payload'])
    #     pprint(msg, depth=3)
    #     print('-----------------------END OF NO BODY EMAILS-------------------------------')

    msgs_calinvites = [msg for msg in msgs if msg['_message_type'] == 'calendar_invite']
    logging.info('num cal invites: ' + str(100*len(msgs_calinvites)/len(msgs)) + '%')
    logging.info('num no body emails: ' + str(100*len(msgs_no_body)/len(msgs)) + '%')
    
    # get messages with no snippets
    # logging.info('---- no snippet msgs ----')
    # msgs_no_snippet = [msg for msg in msgs if msg['m_snippet'] in ['',' ',None]]
    # pprint(msgs_no_snippet, depth=4)


    logging.info("--- %s seconds to execute ---", round((time.time() - START_TIME), 2))
