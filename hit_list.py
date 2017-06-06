import re
from pprint import pprint

def read_file(filepath):
    with open(filepath, 'r') as content_file:
        content = content_file.read()
    return content

# def parse_out_email_address(email_header_item):
#     matches = re.findall(r'<([^@]+?@[^@]+?)>',email_header_item)
#     if len(matches) == 0:
#         matches = re.findall(r'([^\' ,<>]+@[^\' ,<>]+)',email_header_item)
#     if len(matches) == 0:
#         print('- - - - - - - ERROR - - - - - - - ')
#         print('raw email header = %s'%email_header_item)
#         print('- - - - - - - ERROR - - - - - - - ')
#     # print (matches)
#     return matches

def main():
    content = read_file('email_store.txt')
    people = content.split("]•\n[")
    people = [person.replace("'","").replace(" ","").replace("•\n","").split(",") for person in people]
    print('number of people = %d'%len(people))
    emails = [] # for emails
    names = {} # name lookup
    store = {} # for count
    for person in people:
        email = person[0]
        name = person[1]
        if email not in emails:
            emails.append(email)
            store[email] = 1
            names[email] = name
        elif email in emails:
            store[email] += 1
        else:
            print('THIS SHOULD BE IMPOSSIBLE')
    store_prioritised = []
    for key, value in store.items():
        store_prioritised.append([key,value])

    store_prioritised.sort(key=lambda x: x[1]) #,reverse = True
    pprint (store_prioritised)
    print('number of people in store = %d'%len(store_prioritised))


if __name__ == '__main__':
    main()