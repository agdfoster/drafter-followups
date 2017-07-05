'''get_messages.py v2.0 using different method. Does not include enrichment.'''

from datetime import datetime
import logging
from pprint import pformat
import time
from datetime import datetime, timedelta

# import google_auth
from googleapiclient import errors
from googleapiclient.http import BatchHttpRequest

# from gmail_quickstart import get_credentials
import get_gmail_service_obj

# USER = {'googleRefreshToken': '1/tEQsqzKONt7h9BbTsG-x3pWu6XYBt-7UF1m_CxH7nc8'}
# service = google_auth.get_service(USER, 'gmail')
service = get_gmail_service_obj.main()
logging.getLogger('googleapiclient').setLevel(logging. CRITICAL + 10)
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
# . env_vars.sh <<< TO RUN ENV VARS LOCALLY


def define_search_period(no_days_to_back_search):
    '''returns an "AFTER" date string relative to todays date
    for a given number of days in the past 
    NOTE: assume this run in the morning, local time
    NOTE: AFTER date in gmail *includes* that day. E.g, AFTER:2017/01/01 includes email ON 1st jan'''
    now = datetime.today()
    dif = timedelta(days=no_days_to_back_search)
    output_date_for_AFTER = now - dif
    output_string = output_date_for_AFTER.strftime("%Y/%m/%d")
    return output_string

def get_messages_from_dates_and_threads(service, user_id, before=None, after=None, max_results=100):
    ''' Super advanced tech :) we get a list of messages based on a before or after
    time-date (unix or gmail format) and return all messages matching that query
    ACROSS THREADS. I.e, if the most recent message fits the query - the whole thread
    returns. I think. I think that's how gmail works. 
    Note: this function replaces all functionality in get_messages up to enrichment.
    
    Yes, This function is horribly formatted - so shoot me'''

    if not before and not after:
        raise TypeError("no before or after date provided for date query func")
    
    # def msg_ids_from_date_query(service, user_id, query='', after=None, before=None):
    # add dates to the query
    if after:
        if isinstance(after, int):
            # sometimes timestamp is 1000 times larger (miliseconds)
            if after > 1000000000000: after = after/1000
            # format date string in gmail query format
            after = datetime.fromtimestamp(after).strftime('%Y/%m/%d')
        if isinstance(after, str):
            query = 'after:' + after + ' '
    if before:
        if isinstance(before, int):
            # sometimes timestamp is 1000 times larger (miliseconds)
            if before > 1000000000000: before = before/1000
            # format date string in gmail query format
            before = datetime.fromtimestamp(before).strftime('%Y/%m/%d')
        if isinstance(before, str):
            query = 'before:' + before + ' '
    logging.info('searching using query = %s'%query)
    #--------------------------------------------------------------------------------
    # THREAD IDS
    # make query for message/thread IDs
    #--------------------------------------------------------------------------------

    try:
        response = service.users().threads().list(userId=user_id, q=query).execute()
        logging.info('getting message IDs from gmail page 1')
        # cycle through pages
        thread_ids = []
        if 'threads' in response:
            thread_ids.extend(response['threads'])
            pageno = 2
        while 'nextPageToken' in response:
            logging.info('getting message IDs from gmail page %d'%(pageno))
            page_token = response['nextPageToken']
            response = service.users().threads().list(userId=user_id, q=query, pageToken=page_token).execute()
            thread_ids.extend(response['threads'])
            pageno += 1
        logging.info('finished getting gmail msg IDs')
    except errors.HttpError as error:
            logging.info('An error occurred: %s' % error)
    # thread_ids has history ID and snippet, reduce it to just a list of thread_ids.
    thread_ids = [item['id'] for item in thread_ids]
    logging.info('retrieved %d thread_ids'%len(thread_ids))
    # now get the msg_ids for msgs in each of those thread_ids

    # MAX RESULTS
    # if a max results is set, limit the number of batch requests to make.
    if len(thread_ids) > max_results:
        logging.info("found %d threads for query, limiting to %d threads, the max_results param"%(len(thread_ids), max_results))
        thread_ids = thread_ids[:max_results]

    # 1 you could get them one at a time... NAAAH
    # for thread_id in thread_ids:
    #     thread = service.users().threads().get(userId=user_id, id=thread_id).execute()
    #     messages = thread['messages']
        # for msg in messages: 
        #     date = datetime.fromtimestamp(int(msg['internalDate'])/1000).strftime('%Y/%m/%d')
        #     logging.debug(date)
        # logging.info(pformat(thread['messages'], depth=3))

    #--------------------------------------------------------------------------------
    # GET MESSAGES
    # Make a batch request (and throttle it) to get message objects.
    #--------------------------------------------------------------------------------
    # 2 do them in a batch request
    logging.info('starting batch requests for %d threads'%len(thread_ids))

    n = 50 # recommended figure from google for all batch APIs
    sleep = 0.5 # setting to 0 works but unsafe incase of extra fast callbacks. only 10% speed benefits beyond 0.2s in tests

    # chunk up thread id list into lists of lists [[idslist],[idslist]]
    thread_id_chunks = [thread_ids[i:i + n] for i in range(0, len(thread_ids), n)]
    logging.info("thread_ids chunked")

    # get all threads (threads of messages) for those chunks in throttled fashion
    messages = []
    def gmail_callback(request_id, response, exception):
        ''' this is the function that executes one a response from batch request callback returns
        so check the logic below - and know that it will happen for each.'''
        if exception: raise exception
        messages.extend(response['messages'])
    logging.info('gmail callback defined')

    # build then execute batch
    for idx, thread_id_chunk in enumerate(thread_id_chunks):
        batch = BatchHttpRequest() # must be defined inside the loop
        for thread_id in thread_id_chunk:
            # logging.debug(i)
            batch.add(service.users().threads().get(userId='me', id=thread_id), callback=gmail_callback)
        # execute each batch
        batch.execute()

        logging.info('Retrieving gmail API thread batch %d %s'%(idx+1, '('+str((idx+1)*50)+')'))
        time.sleep(sleep)
    # callbacks are Asynchronous so put a pause in that waits for all the chunks to finish
    timer = 0
    timeout = 30 #secs
    batch_request_complete = False
    while not batch_request_complete:
        inp = thread_ids
        out = set([thread['threadId'] for thread in messages]) #unique as getting multiple messages for some threads
        batch_request_complete = len(inp) == len(out)
        time.sleep(0.5)
        # throw an error if it takes too long (30s)
        timer += 0.5
        we_have_been_waiting_too_long = timer == timeout
        if we_have_been_waiting_too_long:
            raise Exception('Alex: Batch request did not complete in %ds'%timeout)
    logging.info('all %d callbacks have been recieved.'%len(messages))
    logging.info('we have %d messages from %d threads.'%(len(messages), len(thread_ids)))


    # OK - we now have a function that get's us a nice big 
    # list of messages based on date of THREAD.
    # logging.debug(pformat(messages, depth=1))
    
    return messages

if __name__ == '__main__':
    after = '2017/06/10'
    before = None
    user_id = 'me'
    get_messages_from_dates_and_threads(service, user_id, after=after, before=before)

    


# logging.debug(pformat(messages, depth=1))
