"""
This script is responsible for parsing the reply

TODO: Test cases to add:
    - 2xlexbo0twt0dobjd6hb5cclx (rb@pipetop.com)
    - 4im225mludcde615fboac8qv (rb@pipetop.com)
    - d4h8hjnu6tcfjzt1tmqhb66i6 (rb@pipetop.com)
    - afiz9mh4vq6nq69ephogw18t0 (rb@pipetop.com)
    - 2cgm0of09svo0ozod34orf896 (rb@pipetop.com)
    - 105i9rnviujhw9n2w9rk75ier (sebastian@woodpecker.co - account_id=6ypy0mmbxn10y86bennr1kkng)
    - 5jb1qh3uc45s5g1awhjut1s8f (wojtek@woodpecker.co)
    - sw3ost0a5qqwaea24l6cz5ig (wojtek@woodpecker.co)
    - 2tiijbtpvp9ptajnujg69grq6 (wojtek@woodpecker.co)
    - Example below
    Brandt,

    Thanks, but we do not provide imaging services.
    Regards,
    John
"""


import sys
import logging

# Necessary for using talon regexes
import regex as re
# import probablepeople


import talon # was throwing an error - NOTE_MARTIN
from talon.signature.bruteforce import extract_signature
# from talon import quotations
import talon.quotations

from . import preprocess_text
from . import regexes
from data import names


logger = logging.getLogger('reply_parser')

logger.setLevel(logging.WARNING)

handler = logging.StreamHandler()
logger.addHandler(handler)


# TODO: Replace with re.escape()
REGEX_SAFE_TRANS = {ord(i): None for i in '()+?$^[]{}|'}


def split_text_on_regex(text, regexp, invert=False):
    """
    Searches the text using the regexp and splits the text (up_to_first_regex_match, rest)

    The optional parameter invert is for when the return object should be (match, rest_of_string)

    TODO: Optional parameter to not match on first (n) lines
    TODO: Optional parameter to strip text or not
    """
    match = re.search(regexp, text)

    if not match:
        return (text, None)

    if invert:
        end_index = match.end()
        return (text[:end_index].strip(), text[end_index:].strip())

    start_index, _ = match.span()

    return (text[:start_index - 1].strip(), text[start_index:].strip())


def get_greeting_name_variants(full_name):
    """
    Get all possible names someone could use in their email greeting, e.g., 'Hi Jonathan', 'Hi Johnny', 'Hi J'
    """

    full_name = full_name.lower() if full_name else ''

    try:
        tagged_person, _ = probablepeople.tag(full_name)
    except probablepeople.RepeatedLabelError:
        # print('Error parsing name "{full_name}"'.format(full_name=full_name))
        return [full_name]

    # print(tagged_person)
    given_name = tagged_person.get('GivenName')
    alternate_names = names.NAMES.get(given_name)
    initial = given_name[0] if given_name else ''


    name_variants = [given_name, initial]
    if alternate_names:
        name_variants = name_variants + alternate_names


    # Remove blanks
    name_variants = [variant for variant in name_variants if variant]

    return name_variants


def extract_greeting(text, to_name=''):
    """Takes the email text and the name of the person being emailed, returns (greeting, body)"""

    name_variants = get_greeting_name_variants(to_name)
    name_variants = [re.escape(variant) for variant in name_variants]
    custom_greeting_regex_string = regexes.GREETING_REGEX % '|'.join(name_variants) if name_variants else regexes.GREETING_REGEX % 'THIS_SHOULD_NEVER_MATCH'
    # custom_greeting_regex = re.compile(custom_greeting_regex_string, re.IGNORECASE | re.MULTILINE | re.VERBOSE)

    try:
        custom_greeting_regex = re.compile(custom_greeting_regex_string, re.IGNORECASE | re.MULTILINE | re.VERBOSE)
    except Exception:
        # print(message)
        logger.error('custom_greeting_regex_string: {custom_greeting_regex_string}'.format(custom_greeting_regex_string=custom_greeting_regex_string))
        logger.error('text: "{text}", to_name: "{to_name}"'.format(text=text, to_name=to_name))
        sys.exit(1)

    # Invert=True because we want the split to start after the match object, not at the start of it
    (greeting, body) = split_text_on_regex(text, custom_greeting_regex, invert=True)

    if not body:
        # The greeting regex has no matched
        return (text, text)

    return (greeting, body)


def get_first_name(name):
    """Returns the first name for a given name"""
    match = re.search(r'^\w+', name)

    return match.group() if match else ''


def get_initials(full_name):
    """
    Get a person's initials
    """

    try:
        (tagged_person, name_type) = probablepeople.tag(full_name)
    except probablepeople.RepeatedLabelError:
        # print('Error parsing name "{full_name}"'.format(full_name=full_name))
        return []


    if name_type != 'Person':
        return []

    # TODO: Add in tests for full_name like '(Something) John Smith' and 'simone davalos (slack)'
    given_name_initial = tagged_person['GivenName'].translate(REGEX_SAFE_TRANS)[0] if tagged_person.get('GivenName') else tagged_person.get('FirstInitial', '').translate(REGEX_SAFE_TRANS)[:1]
    middle_name_initial = tagged_person['MiddleName'].translate(REGEX_SAFE_TRANS)[0] if tagged_person.get('MiddleName') else tagged_person.get('MiddleInitial', '').translate(REGEX_SAFE_TRANS)[:1]
    surname_initial = tagged_person['Surname'].translate(REGEX_SAFE_TRANS)[0] if tagged_person.get('Surname') else tagged_person.get('LastInitial', '').translate(REGEX_SAFE_TRANS)[:1]
    nickname_initial = tagged_person.get('Nickname', '')


    initials = [
        given_name_initial + middle_name_initial + surname_initial,
        given_name_initial + surname_initial,
        nickname_initial + surname_initial if nickname_initial else None,
        given_name_initial,
        nickname_initial,
    ]

    filtered_initials = set([initial for initial in initials if initial])

    return filtered_initials


def get_initals_for_regex(full_name):
    """
    Gets a person's initials in a form acceptable for a regex, i.e., (A(,|$)|AF|AGDF)

    - Single initials must have punctuation or EOL afterwards
    - Initials variants:
        -- AGDF
        -- A.G.D.F.?
        -- A G D F
    """
    possible_initials = get_initials(full_name)

    # Make safe for regex by removing bad characters
    possible_initials = set([initals.translate(REGEX_SAFE_TRANS) for initals in possible_initials])

    initials_regexes = []

    for initials in possible_initials:
        if len(initials) == 1:
            # TODO: Think about acceptable punctuation
            initials_regexes += [r'%s[,!]?[ ]*$' % initials]
        else:
            initials_regexes += [r''.join(initials)]
            initials_regexes += [r' '.join(initials)]
            initials_regexes += [r'.'.join(initials) + r'.?']


    if not initials_regexes:
        return ''

    # Don't do this here, it is done later
    # initials_regexes = list(map(re.escape, initials_regexes))

    initials_regex_string = r'(' + r'|'.join(initials_regexes) + r')'

    return initials_regex_string



def get_name_regex(full_name, email):
    """
    Get bespoke regex for matching a person's name as a signature
    TODO: Does the greeting variant need to be any different?
    TODO: What about 'Jane & John' type signoffs - see Alex's message 16wwe57ropc7pcos81h17lekr
    """

    full_name = full_name.lower() if full_name else ''

    first_name = get_first_name(full_name)


    initials_for_regex = get_initals_for_regex(full_name)
    first_part_of_email = email.split('@')[0]

    # TODO: This could cause issues - needs to be tested
    # potential_names = list(map(re.escape, [first_part_of_email, full_name, first_name, initials_for_regex]))
    potential_names = [re.escape(first_part_of_email), re.escape(full_name), re.escape(first_name), initials_for_regex]
    if names.NAMES.get(first_name.lower()):
        potential_names = potential_names + names.NAMES.get(first_name.lower())

    # Remove any nulls
    potential_names = [name for name in potential_names if name]

    custom_name_regex = regexes.NAME_BASED_SIGNOFF_REGEX % '|'.join(potential_names)
    # print(custom_name_regex)
    try:
        name_regex = re.compile(custom_name_regex, re.IGNORECASE | re.MULTILINE)
    except Exception as exc:
        logger.error('custom_name_regex: {custom_name_regex}'.format(custom_name_regex=custom_name_regex))
        logger.error('full_name: "{full_name}", email: "{email}"'.format(full_name=full_name, email=email))
        logger.error('Error: exiting')
        raise exc


    # print(name_regex)
    return name_regex


def name_based_signoff_stripper(text, from_name, email):
    """Takes an email and returns (body, signoff)"""
    name_based_regex = get_name_regex(from_name, email)

    match = re.search(name_based_regex, text)
    if not match:
        return (text, None)

    (start_index, _) = match.span()

    index_of_first_newline = text.find('\n')
    if index_of_first_newline == -1 or start_index < index_of_first_newline:
        # Alleged signature starts on the first line - this cannot be right
        return (text, None)

    body = text[:start_index - 1].strip()
    signature = text[start_index:]

    return (body, signature)


def signoff_stripper(text, from_email='', from_name=''):
    """
    Takes an email and returns (body, signoff)
    """

    # Leading whitespace can hinder regexes using '^'
    text = text.strip()

    body, signoff = split_text_on_regex(text, regexes.RE_SIGNATURE_IMPROVED)
    body, signoff_2 = split_text_on_regex(body, regexes.BROAD_SIGNOFF_REGEX)
    body, signoff_3 = split_text_on_regex(body, regexes.EVERYTHING_AFTER_PIPE_REGEX)

    signoff_4 = ''
    if from_name:
        body, signoff_4 = name_based_signoff_stripper(body, from_name, from_email)


    signoff = '\n'.join(map(str, filter(None, [signoff, signoff_2, signoff_3, signoff_4])))

    return (body, signoff)


def temp_because_talon_not_working(plain):
    """
    This function was created because we couldn't get talon to work for certain messages.
    However, it does have regexes which match 'on <date> <person> wrote'
    """

    plain, _ = split_text_on_regex(plain, talon.quotations.RE_ON_DATE_SMB_WROTE)
    plain, _ = split_text_on_regex(plain, talon.quotations.RE_ON_DATE_WROTE_SMB)


    return plain



def parse_email(whole_email_html='', whole_email_plain='', from_email='', from_name='', to_name=''):
    """
    Returns {'greeting': 'xxx', 'body': 'yyy', 'signoff': 'zzz', 'signature': 'aaa'}

    TODO: Think about returning quoted_text too
    """


    if not (whole_email_html or whole_email_plain):
        logger.debug('No text passed in to parse_email')
        # raise ValueError('Must include either plain text or html email')
        whole_email_plain = ''


    if whole_email_html:
        try:
            reply_only_html = talon.quotations.extract_from_html(whole_email_html)
        except ValueError:
            logger.warning('Error using talon to extract quotations from html')
            return None


        reply_only_text = preprocess_text.html_to_text(reply_only_html)
    else:
        reply_only_text = whole_email_plain




    # This is for emails that use '>' instead of <blockquote>
    reply_only_text = talon.quotations.extract_from_plain(reply_only_text)
    # Temporary function to handle 'On <date> <person> wrote:'
    reply_only_text = temp_because_talon_not_working(reply_only_text) # MARTIN

    body_text, signature_text = extract_signature(reply_only_text)
    body_text, signoff_text = signoff_stripper(body_text, from_email=from_email, from_name=from_name)
    greeting_text, body_text = extract_greeting(body_text, to_name=to_name)


    # Incase greeting extractor has been too greedy (remove body from greeting)
    if greeting_text.endswith(body_text):
        greeting_text = greeting_text[:-len(body_text)]

    # body_text = preprocess_text.postprocess_reply_only(body_text)
    return {
        'greeting': greeting_text,
        'body': body_text,
        'signoff': signoff_text,
        'signature': signature_text,
        # TODO: This is a hack
        'whole': '\n'.join([greeting_text, body_text, signoff_text])
    }


def get_reply(whole_email_html, from_email='', from_name='', to_name='', debug=False):
    """
    Extract only reply from an email
    """
    try:
        reply_only_html = talon.quotations.extract_from_html(whole_email_html)
    except ValueError:
        logger.warning('Error using talon to extract quotations from html')
        return ''

    if debug:
        logger.debug('\n\nreply_only_html: {reply_only_html}'.format(reply_only_html=reply_only_html))

    reply_only_text = preprocess_text.html_to_text(reply_only_html)
    if debug:
        logger.debug('\nreply_only_text: {reply_only_text}'.format(reply_only_text=reply_only_text))


    return get_reply_from_plain(reply_only_text, from_email=from_email, from_name=from_name, to_name=to_name, debug=debug)


def get_reply_from_plain(reply_only_text, from_email='', from_name='', to_name='', debug=False):
     # This is for emails that use '>' instead of <blockquote>
    reply_only_text = talon.quotations.extract_from_plain(reply_only_text)
    if debug:
        logger.debug('\nreply_only_text extract_from_plain: {reply_only_text}'.format(reply_only_text=reply_only_text))


    reply_only_text = temp_because_talon_not_working(reply_only_text)
    if debug:
        logger.debug('\nreply_only_text temp_because_talon_not_working: {reply_only_text}'.format(reply_only_text=reply_only_text))


    # This is necessary but the ideal solution is to
    reply_only_text = preprocess_text.remove_chevrons(reply_only_text)
    if debug:
        logger.debug('\nreply_only_text chevrons_removed: {reply_only_text}'.format(reply_only_text=reply_only_text))


    body_text, _ = extract_signature(reply_only_text)

    if debug:
        logger.debug('\nsignature_extracted: {body_text}'.format(body_text=body_text))

    # if body_text == reply_only_text:
        # If talon didn't find a signature, use a more aggressive stripper

    # For now, default to the more aggressive stripper
    body_text, _ = signoff_stripper(body_text, from_email=from_email, from_name=from_name)
    if debug:
        logger.debug('\nsignoff_stripped: {body_text}'.format(body_text=body_text))

    # TODO: What about storing the greeting?
    _, body_text = extract_greeting(body_text, to_name=to_name)
    if debug:
        logger.debug('\ngreeting_extracted: {body_text}'.format(body_text=body_text))


    body_text = preprocess_text.postprocess_reply_only(body_text)
    if debug:
        logger.debug('\npostprocessed: {body_text}'.format(body_text=body_text))

    return body_text
