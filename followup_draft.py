'''slave function for drafting followups.
1. select random draft, allow flexibility for classification later
2. take a list of msg_ids as input and draft as replies to them
3. take a 'to' and 'cc' field as input and include those in the draft
4. take a list of msg_ids and user email as input (rather than one at a time) and send an email
to the user to let them know their drafts are ready. '''


def draft_followups_main(user_email, draft_target_msg_ids, to, cc, ):
    '''slave function for drafting followups.
    1. select random draft, allow flexibility for classification later
    2. take a list of msg_ids as input and draft as replies to them
    3. take a 'to' and 'cc' field as input and include those in the draft
    4. take a list of msg_ids and user email as input (rather than one at a time) and send an email
    to the user to let them know their drafts are ready. '''
    raise NotImplementedError

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

from apiclient import errors

def CreateDraft(service, user_id, message_body):
  """Create and insert a draft email. Print the returned draft's message and id.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    message_body: The body of the email message, including headers.

  Returns:
    Draft object, including draft id and message meta data.
  """
  try:
    message = {'message': message_body}
    draft = service.users().drafts().create(userId=user_id, body=message).execute()

    print( 'Draft id: %s\nDraft message: %s'%(draft['id'], draft['message']))

    return draft
  except errors.HttpError as error:
    print( 'An error occurred: %s' % error)
    return None

def CreateMessage(sender, to, subject, message_text):
    """Create a message for an email.
    Args:
        sender: Email address of the sender.
        to: Email address of the receiver.
        subject: The subject of the email message.
        message_text: The text of the email message.
    Returns:
        An object containing a base64url encoded email object.
    """
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    return {'raw': base64.urlsafe_b64encode(message.as_string())}

def main():
    CreateMessage('agdfoster@gmail.com', 'foster@draft-ai.com','oh hey!', 'this is a draft')

main()