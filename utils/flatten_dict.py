''' takes a multi level dict and flattens it into a single level dict
    > cant handle lists of dicts within dicts'''
import collections
from pprint import pprint

def flatten_dict(dctnry, parent_key='', sep='_'):
    ''' takes a multi level dict and flattens it into a single level dict
    > cant handle lists of dicts within dicts'''
    items = []
    for k, v in dctnry.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

if __name__ == '__main__':
    diction = {'a': 1, 'b': {'c':2, 'd':3}}
    pprint(flatten_dict(diction))