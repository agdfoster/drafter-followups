'''slave function for drafting followups.
1. select random draft, allow flexibility for classification later
2. take a list of msg_ids as input and draft as replies to them
3. take a 'to' and 'cc' field as input and include those in the draft
4. take a list of msg_ids and user email as input (rather than one at a time) and send an email
to the user to let them know their drafts are ready. '''

# step 1 - get gmail to draft anything
# from https://developers.google.com/gmail/api/v1/reference/users/drafts/create
import base64
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import mimetypes
import os
from pprint import pprint
import html2text
import logging

from apiclient import errors

def CreateDraft(service, user_id, mime_message_to_send):
  """Create and insert a draft email. Print the returned draft's message and id.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    message_body_b64: The body of the email message, including headers.

  Returns:
    Draft object, including draft id and message meta data.
  """
  try:
    
    draft = service.users().drafts().create(userId=user_id, body=mime_message_to_send).execute()

    logging.info( 'Draft id: %s\nDraft message: %s'%(draft['id'], draft['message']))

    return draft
  except errors.HttpError as error:
    logging.info( 'An error occurred: %s' % error)
    logging.info('if Json returned not found - this is probably that you are passing thread ids that dont exist. Probably because youre getting messages from a different account the one youre now running on')
    return None

def create_mime_msg(sender, to_email, subject, msg_html, msg_plain, thread_id):
    """Create a message for an email.
    Args:
        sender: Email address of the sender.
        to: Email address of the receiver.
        subject: The subject of the email message.
        message_text: The text of the email message.
    Returns:
        An object containing a base64url encoded email object.
        NOTE this is the object that create_draft takes as input
    """
    msg = MIMEText(msg_plain)
    # message['to'] = to
    # message['from'] = sender
    # message['subject'] = subject
    # base64_encoded_message_string = base64.urlsafe_b64encode(bytes(message.as_string(), 'utf-8')).decode('utf-8')

    # msg = MIMEMultipart('alternative') # TODO MARTIN 's code uses this... why multi part alternative?
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = to_email
    # msg['threadId'] = '15ce8ebaa4f489a3'
    # msg.attach(MIMEText(msg_plain, 'plain'))
    # msg.attach(MIMEText(msg_html, 'html'))
    logging.info('----------------------')
    for k, v in msg.items():
        logging.info(str(k) + ' = ' + str(v))
        logging.info('thread id = '+thread_id)
    logging.info('----------------------')
    raw = base64.urlsafe_b64encode(bytes(msg.as_string(), 'utf-8')).decode('utf-8')
    message = {'message': {'raw': raw, 'threadId': thread_id}}
    return message

'''NOTE OK Drafts not attaching.
1. potentially I'm getting the info wrong someohow - getting and setting might fix. Have to do it anyway.
2. potentially I need to set the response thingy (draft reply to a message)
3. Potentially lack of quoted text is the issue.
4. Potentially the threadId is not supposed to be part of the MIME object.
NOTE - AHA. OK, two errors: 
1. I'm using thread_ids from the wrong account.
2. threadId DOES NOT go into the mime object, it's passed in next to 'raw'.
3. We can attach directly to the thread, no need to specify which message to draft for.
'''

def greeting_generator(greeting_raw):
    if len(greeting_raw) > 1:
        greeting = greeting_raw
    else:
        greeting = 'Hi,'
    return greeting

def followup_body_generator(fname, sname, greeting, type=1):
    ''' generates a plain and html body for the followup
    based on a list of followups. Chooses which one randomly'''
    # generate using http://www.textfixer.com/html/convert-text-html.php
    msg1 = "<p>{}</p><p>Just checking in on the below.</p><p>Best,</p><p>{}</p>".format(greeting, fname)
    return msg1

def main(service, user_email, msg_to_reply_to, fname, sname):
    ''' master function - see file description'''
    msg = msg_to_reply_to
    # get values for building email from msg
    From = user_email
    to = msg['h_to_email_primary']
    # cc = msg['cc'] # TODO - put everyone in cc back in cc.
    subject = msg['m_subject']
    greeting = greeting_generator(msg['m_body']['greeting'])
    body_html = followup_body_generator(fname, sname, greeting)
    body_plain = html2text.html2text(body_html)
    body_for_quoted_text = msg['m_body']['html']
    thread_id = msg['id_thread']

    # create raw mime message + thread id object for sending
    mime = create_mime_msg(From, to, subject, body_html, body_plain, thread_id)
    # push the draft!
    x = CreateDraft(service, user_email, mime) # draft created in side effect
    if x: return True
    else: return False
    # function completed

if __name__ == "__main__":
    # test message
    # as it's followups, we only need to look at who the message is 'to'
    msg = {
        'h_to_email_primary': 'test@test.com',
        'id_thread': '15cee72dfc06d3d3',
        'm_subject': 'Google APIs Explorer connected to your Google Account',
        'm_body': {'html': 'Hi there, this is a message that needs gollowing up to'},
    }
    import get_gmail_service_obj
    service = get_gmail_service_obj.main()

    # call master function for agdfoster@gmail.com
    main('agdfoster@gmail.com', msg, 'Alex', 'Foster')





# TODO 
''' 
1. quoted text
'''