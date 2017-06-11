import get_messages
from pprint import pprint
from utils.deep_get import deep_get, deep_get_all

from gmail_quickstart import get_credentials
service = get_credentials()





def print_all_mimes(message):
    print('-----getting mimes-----')
    parts = get_messages.get_parts(message)
    if parts:
        # Get Mimetypes
        mimes = [deep_get_all(part, 'mimeType') for part in parts]
        mimes = get_messages.flatten(mimes)
        print('mimetypes found = ' + str(mimes))
    if not parts:
        print('-----couldnt find parts - looking in message obj-----')
        mimes = deep_get_all(message, 'mimeType')
        print('mimetypes found = ' + str(mimes))

# ID = '15ba92dab476396e' # calendar invite
# ID = '156d56250d743d45' #multipart/alternative no snippet
# ID = '15c1c81ae7266fc3'
# ID = '15c1c81ae7266fc3' # CSV Error
ID = '15a245d53b8a8947' # stripper error
message = get_messages.get_single_message(service, 'me', ID)



header_subject = get_messages.get_subject(message)
# print(header_subject)
is_fwd = header_subject.startswith('Fwd:')
# print(is_fwd)
enriched_msg = get_messages.enrich_message(message)
del enriched_msg['GMAIL']
pprint(enriched_msg)

cat = get_messages.categorize_message(message)
print('category = ' + str(cat))

# temp_b6_string = ''
# print(get_messages.decode_b64(temp_b6_string))

# print(get_messages.decode_b64(deep_get(message,'data')))

# print_all_mimes(message)