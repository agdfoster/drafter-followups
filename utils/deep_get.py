



def deep_get_all(search_dict, get_key):
    '''recursively searches through dictionary looking for a
    match with the key given then returns a list of values for any matches.
    > should find at any depth
    > must be passed a dictionary, not list of dictionaries
    > returns blank array if it finds nothing
    > will also loop through lists found (warning: however large)
    > returns only the highest level match'''
    fields_found = []
    for key, value in search_dict.items():

        if key == get_key:
            fields_found.append(value)
        if isinstance(value, dict):
            results = deep_get_all(value, get_key)
            for result in results:
                fields_found.append(result)

        if isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    more_results = deep_get_all(item, get_key)
                    for another_result in more_results:
                        fields_found.append(another_result)
    return fields_found

def deep_get(search_dict, get_key):
    '''recursively searches through dictionary looking for a
    match with the key given then returns that key's value.
    > Returns ONE result, use deep_get_all for list of results
    > WARNING: does depth first, not bredth first.
    > returns None if nothing found
    > should find at any depth
    > must be passed a dictionary, not list of dictionaries
    > will also loop through lists found (warning: however large)
    > returns only the highest level match'''
    matches_list = deep_get_all(search_dict, get_key)
    # return None instead of blank array
    if len(matches_list) == 0:
        return None
    elif len(matches_list) > 0:
        return matches_list[0]

if __name__ == '__main__':
    def test_find_dict_item():
        '''lazy test'''
        example_dictionary = {
            'a':{
                '1': 'no',
                '2':[
                    {'part': 'you win1!', '2': 'no'},
                    {'2': 'no'}
                    ],
                '3': 'no'
            },
            'b': 'no',
            'c': {'part': 'you win2!', '2': 'no'},
            'd': {'ffff': {'e': {'part': 'you win3!', '2': 'no'}, '2': 'no'}, '2': 'no'},
            'e': {'part': {'e': {'part': 'you win4!', '2': 'no'}, '2': 'no'}, '2': 'no'}
            }

        # doesn't find it
        print('get finds: '+ str(example_dictionary.get('part')))
        # does find it
        print('func ONE finds: '+ str(deep_get(example_dictionary, 'part')))
        print('func ALL finds: '+ str(deep_get_all(example_dictionary, 'part')))
        # TESTS
        # misspell the key
        # put a list of dicts in there
        # 
    test_find_dict_item()