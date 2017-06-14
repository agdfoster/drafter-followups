''' file making regex's a little easier to use :) '''
# https://docs.python.org/3/howto/regex.html

# first I want versions of Google Sheets regex's. Very simple.
# regex.replace (string, regex, flags)
# > flags are just the letters.
# regex.match > returns true if there is a match.
# regex.extract > returns first matching sub string if there is a match
# regex.extract_all > returns all matches from matching groups

import re

def match(string, regex_string_literal, flags=0):
    ''' returns true / false based on re match'''
    reg = re.compile(regex_string_literal, flags)
    # get match object, use search as match is anchored at string start
    match_object = reg.search(string)
    # now query the match object for what you want
    # group, start, end, span are options. span = start+end tuple
    if match_object:
        return True
    if not match_object:
        return None

def extract(string, regex_string_literal, flags=0):
    ''' returns true / false based on re match'''
    
    reg = re.compile(regex_string_literal, flags=flags)
    # get match object, use search as match is anchored at string start
    match_object = reg.search(string)
    # now query the match object for what you want
    # group, start, end, span are options. span = start+end tuple
    if match_object:
        return match_object.group()
    if not match_object:
        return ''


# tests
if __name__ == '__main__':
    tests = [
        'Lucy White <Lucy.White@resurgo.org.uk>',
        'Alex Foster <foster@drafterhq.com>',
        'measdojasd'
        ]
    regex = r'<([^@]+?@[^@]+?)>'
    #https://regex101.com/r/N5FEAt/1
    for test in tests:
        print('match = '+ str(match(test, regex, re.I|re.X|re.M)))
        print('extrt = ' + str(extract(test, regex, re.I|re.X)))
