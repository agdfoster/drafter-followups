''' makes csv files for spreadsheet interrogation'''
import csv
from pprint import pprint

import get_messages
from get_messages import get_msgs_from_query, enrich_message
from utils.flatten_dict import flatten_dict
from gmail_quickstart import get_credentials
service = get_credentials()


def write_csv_from_list_dicts(dicts, filename='_CSV.csv'):
    ''' takes flattened dicts list and writes a CSV file'''
    keys = dicts[0].keys()
    with open(filename, 'w') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(dicts)


messages = get_msgs_from_query(service, 'me', 'from:me', 500, start=100)
msgs = [enrich_message(message) for message in messages]
# remove gmail part
for msg in msgs:
    del msg['GMAIL']
# flatten for CSV reader
msgs_flat = [flatten_dict(msg) for msg in msgs]

# check it visually
# pprint(msgs_flat, depth=4)

# write csv
write_csv_from_list_dicts(msgs_flat, '_CSV.csv')