''' desc '''
from pprint import pprint

from get_messages import get_msgs_from_query, enrich_message
from text_processing.reply_parser import parse_email
from gmail_quickstart import get_credentials
service = get_credentials()


# msg = {
#         'GMAIL': {'spacer': {'spacer': message}},
#         'h_from': header_from,
#         'h_to': header_to,
#         'id_message': message_id,
#         'id_thread': thread_id,
#         'date_sent': date_sent,
#         'm_snippet': snippet,
#         'm_body_html': {'spacer': body_html},
#         'm_body_plain': {'spacer': body_plain},
#         'm_body_plain_no_breaks': body_plain_no_breaks,
#         '_message_type': message_type
#     }

messages = get_msgs_from_query(service, 'me', 'from:me', 1, start=0)
msgs = [enrich_message(message) for message in messages]

for msg in msgs:
    whole_email_html = msg['m_body_html']['spacer']
    whole_email_plain = msg['m_body_plain']['spacer']
    from_email = msg['h_from'][0][0]
    from_name = msg['h_from'][0][1]
    to_name = msg['h_to'][0][1]
    parsed_email = parse_email(whole_email_html, whole_email_plain, from_email, from_name, to_name)
    print('----------------------')
    pprint(parsed_email)