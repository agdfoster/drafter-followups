"""
This program preprocesses text for NLP

Regexes are taken from https://docs.google.com/spreadsheets/d/1JevK6UwMoCWWHjxuzd--DrM1UgTlRYCrwiwOtydmeFE
"""

import itertools
import html
import logging
import warnings

# Necessary for using talon regexes
import regex as re
import phonenumbers
import html2text
# import textacy
from ftfy import fix_text
import unidecode

from . import regexes
from ..utilities import timezones
from ..text_processing import formatters


logger = logging.getLogger('preprocess_text')
logger.setLevel(logging.WARNING)

handler = logging.StreamHandler()
logger.addHandler(handler)


H = html2text.HTML2Text()
H.body_width = 0
H.ignore_links = True
H.ignore_anchors = True
H.ignore_images = True
H.ignore_emphasis = True
H.unicode_snob = True
# H.single_line_break = True
H.escape_all = True


# GSheets maxes out at 50k chars in a single cell
# Less characters will help spreadsheet efficiency
MAX_CHARS_FOR_SPREADSHEET = 10000



FIRSTSECONDTHIRD_TOKEN = '1st2nd3rd'
RELATIVE_TIME_TOKEN = 'RELATIVE'
NUMERIC_TIME_TOKEN = 'NUMERIC_TIME'
# Deliberate misspelling to avoid other regexes
DAY_TOKEN = 'DAIOFWEEK'
# Deliberate misspelling to avoid other regexes
MONTH_TOKEN = 'MNTH'
TIME_PERIOD_2_TOKEN = 'PERIOD_2'
TIME_PERIOD_TOKEN = 'PERIOD'


REPLACEMENTS = {
    regexes.TIME_PERIOD_REGEX: TIME_PERIOD_TOKEN,
    regexes.TIME_PERIOD_2_REGEX: TIME_PERIOD_2_TOKEN,
    regexes.MONTH_REGEX: MONTH_TOKEN,
    regexes.DAY_REGEX: DAY_TOKEN,
    regexes.NUMERIC_TIME_REGEX: NUMERIC_TIME_TOKEN,
    regexes.RELATIVE_TIME_REGEX: RELATIVE_TIME_TOKEN,
    regexes.FIRSTSECONDTHIRD_REGEX: FIRSTSECONDTHIRD_TOKEN,
}





def replace_all_time_periods(text):
    """Perform all replacements"""
    replaced = text

    for regexp, replacement in REPLACEMENTS.items():
        replaced = re.sub(regexp, replacement, replaced)

    return replaced


def format_text_for_spreadsheet(text):
    """Replace newlines and ensure doesn't exceed max length for cell"""
    replaced_newlines = text.replace('\n', '\t'*75)
    # 50k is the max num of chars in GSheets cell
    truncated_text = replaced_newlines[0:MAX_CHARS_FOR_SPREADSHEET]

    return truncated_text


def replace_phone_numbers(text, replacement='PHONE_NUMBER'):
    """Replaces all phone numbers with a replacement string - uses libphonenumber"""
    matches = get_phone_number_matches(text)

    processed_text = text

    for match in matches:
        processed_text = processed_text.replace(match, replacement)

    return processed_text


def get_phone_number_matches(text):
    """Return all potential phone numbers that libphonenumber guesses"""

    # print(text)

    all_matches = itertools.chain(*[
        # International format
        phonenumbers.PhoneNumberMatcher(text, None),
        phonenumbers.PhoneNumberMatcher(text, 'GB'),
        phonenumbers.PhoneNumberMatcher(text, 'US'),
        phonenumbers.PhoneNumberMatcher(text, 'LB'),
        phonenumbers.PhoneNumberMatcher(text, 'AE'),
    ])

    return set([match.raw_string for match in all_matches])


def replace_all_currency_instances(text):
    """Replaces all instances of currency (e.g., '£12', '15USD', etc.) with a replacement string"""

    return re.sub(regexes.CURRENCY_REGEX, 'CURRENCY_INSTANCE', text)


def replace_all_sys_generated_times(text):
    """Replaces all instances of system generated times (e.g., 'Dec 12, 15/02/2015 at 15:04', etc.) with a replacement string"""

    return re.sub(regexes.SYSTEM_GENERATED_TIMES, 'SYS_GEN_TIME', text)


def preprocess_text(text, currency=False, phone_numbers=False, no_urls=False, no_emails=False, no_sys_gen_times=False):
    """Wrapper for all preprocessing steps"""


    text = textacy.preprocess.preprocess_text(text, no_urls=no_urls, no_emails=no_emails)


    if no_sys_gen_times:
        text = replace_all_sys_generated_times(text)

    if currency:
        text = replace_all_currency_instances(text)

    if phone_numbers:
        text = replace_phone_numbers(text)

    return text


def markdown_to_plain_text(markdown):
    """
    https://daringfireball.net/projects/markdown/syntax#backslash

    https://regex101.com/r/pY0gB6
    """

    plain_text = re.sub(regexes.MARKDOWN_REGEX, '\\1', markdown)

    return plain_text


def custom_transliteration(text):
    """
    Unidecode has erroneous translations for some characters, e.g., 'ᐧ'
    """

    return text.replace('ᐧ', '')


def html_to_markdown(html_text):
    """
    Error safe html_to_text using html2text
    """
    try:
        markdown_with_encoding = H.handle(html_text)
    # except html.parser.HTMLParseError:
        # markdown_with_encoding = ''
    except AssertionError as exc:
        logger.warning(exc)
        markdown_with_encoding = ''
    except:
        markdown_with_encoding = ''

    return markdown_with_encoding


def html_to_text(html_text):
    """
    Converts html to text through markdown (using html2text)

    TODO: There are issues with this.  For example, spaces being parsed as newlines due to
    HTML idiosyncrasies and then being removed by parsing to concatenate words together
     - see Alex's email 1cyis909lfairm6qe15huukyn
    """
    markdown_with_encoding = html_to_markdown(html_text)

    # e.g., &amp; to &
    markdown = html.unescape(markdown_with_encoding)

    plain_text = markdown_to_plain_text(markdown)

    # Remove unicode (it affects the regexes)
    # unicode_fixed = textacy.preprocess.fix_bad_unicode(plain_text)
    unicode_fixed = fix_text(plain_text, normalization='NFC')
    processed = custom_transliteration(unicode_fixed)
    # processed = textacy.preprocess.transliterate_unicode(processed)
    processed = unidecode.unidecode(processed)


    # Is this necessary?
    # plain_text = remove_leading_and_trailing_whitespace_from_paragraph(plain_text)

    return processed


def remove_whitespace_from_para(text):
    """
    Trims each line, not just before and after the paragraph
    """

    if not text:
        return ''

    return '\n'.join([line.strip() for line in text.split('\n')])


def postprocess_reply_only(text):
    """Carry out the necessary postprocessing after the reply has been extracted"""
    # The order of these functions is important to ensure that 'S1\n\n \n\nS2' does not become 'S1 S2'
    # text = preprocess_reply(text)

    fixed = remove_whitespace_from_para(text)
    # normalised = textacy.preprocess.normalize_whitespace(fixed)
    NONBREAKING_SPACE_REGEX = re.compile(r'(?!\n)\s+')
    LINEBREAK_REGEX = re.compile(r'((\r\n)|[\n\v])+')
    normalised = NONBREAKING_SPACE_REGEX.sub(' ', LINEBREAK_REGEX.sub(r'\n', text)).strip()

    return normalised


def remove_chevrons(text):
    """Aggressive chevron (>) remover - this is necessary to allow signature extraction to work properly"""
    return re.sub(regexes.CHEVRON_REGEX, '', text)


def preprocess_reply(text):
    """
    TODO:
        - Create version with delimiter (' ∫ '?) for newlines

        Note: Needs testing on body (as opposed to body_for_spreadsheet which it is being used on)
    """

    # whitespace_normalised = textacy.preprocess.normalize_whitespace(text)
    # unicode_fixed = textacy.preprocess.fix_bad_unicode(text, normalization=u'NFC')

    # processed = textacy.preprocess.transliterate_unicode(unicode_fixed)
    processed = textacy.preprocess.unpack_contractions(text)


    # For some reason this was removing newlines
    # processed = textacy.preprocess.preprocess_text(unicode_fixed, **{
    #     # 'lowercase': True,
    #     'transliterate': True,
    #     'no_urls': False,
    #     'no_emails': False,
    #     'no_phone_numbers': False,
    #     'no_numbers': False,
    #     'no_currency_symbols': False,
    #     'no_punct': False,
    #     'no_contractions': True,
    # })


    # Remove lines without words
    # processed = regex.sub(LINES_WITHOUT_WORDS_REGEX, '', processed)


    return processed




def replace_entities_in_text(text):
    """
    Uses spaCy to tag named entities and put them into text.

    e.g., 'Shall we go to China this summer?' => 'Shall we go to __gpe__ __date__ __date__?'
    """

    doc = textacy.texts.TextDoc(text, lang='en')

    # entity_tagged = ' '.join(['__{0}__'.format(span.ent_type_.lower()) if span.ent_type_ else span.text for span in doc]).strip()

    tokens = ['__{0}__'.format(span.ent_type_.lower()) + span.whitespace_ if span.ent_type_ else span.text_with_ws for span in doc]
    entity_tagged = ''.join(tokens)

    return entity_tagged


# def detect_lang(text):
#     """
#     Language detection using Google Chromium's embedded compact language detection library (through cffi)
#     """
#     with warnings.catch_warnings():
#         warnings.simplefilter('ignore')
#         return textacy.text_utils.detect_language(text)
#     # return langdetect.detect(text)


# ####################
# wit.ai preprocessing
# ####################

day_modifiers_regex = r'(on[ ]|next[ ]|this[ ]|(the[ ])?(first|second|third|fourth|following|coming|last)[ ])'
day_regex = r'\b(mon(day)?|tue(sday)?|wed(nesday|s)?|thu(r(sday)?)?|fri(day)?|sat(urday)?|sun(day)?|today|tomorrow)\b'
named_time_period_regex = r'(afternoon|morning|\bmorn\b|evening|\beve\b|midd?ay)'
# well_formed_time_regex = r'(1[0-9]|2[0-4]|0?[1-9]|00|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)[ ]?[\:\. ][ ]?([0-5][0-9]|fifteen|thirty|fou?rty ?five)(?:\b|$|,\b| ?[aApP][mM]\b)'

# TODO: Add Monday 1st August, Monday 3 July etc.
days_with_modifiers_regex = r'{day_modifiers_regex}{day_regex}'.format(day_modifiers_regex=day_modifiers_regex, day_regex=day_regex)

days_with_optional_modifiers_before_and_after_regex = r'{day_modifiers_regex}?{day_regex}([ ]{named_time_period_regex})?'.format(day_modifiers_regex=day_modifiers_regex, day_regex=day_regex, named_time_period_regex=named_time_period_regex)


first_half_of_time_regex = r'(1[0-9]|2[0-4]|0?[1-9]|00|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)'
second_half_of_time_regex = r'([0-5][0-9]|fifteen|thirty|fou?rty[ ]?five)'
am_pm_oclock_regex = r'([ ]?(am|pm)|[ ]?o\'?[ ]?clock)'

after_or_before_lone_number_regex = r'(?P<after_before>(before|after)[ ])(?P<lone_number>{first_half_of_time_regex})[ ](?P<day>{day_modifiers_regex}?{day_regex})'.format(first_half_of_time_regex=first_half_of_time_regex, day_modifiers_regex=day_modifiers_regex, day_regex=day_regex)

potential_time_regex = r'''(
  {first_half_of_time_regex}([ ]?[\:\. ]?[ ]?{second_half_of_time_regex})?({am_pm_oclock_regex})?
)(\b|$|,\b)'''.format(**locals())

month_date = r'(1[0-9]|[2-3]0|[2-3]?1|2?2|2?3|2?[4-9])'
ordinal_regex = r'(1[0-9]th|[2-3]0th|[2-3]?1st|2?2nd|2?3rd|2?[4-9]th)'
potential_ordinal = r'(1[0-9](th)?|[2-3]0(th)?|[2-3]?1(st)?|2?2(nd)?|2?3(rd)?|2?[4-9](th)?)'

well_formed_time_regex = r'''(
  {first_half_of_time_regex}[ ]?[\:\. ]?[ ]?{second_half_of_time_regex}({am_pm_oclock_regex})?
  |
  {first_half_of_time_regex}{am_pm_oclock_regex}
)(\b|$|,\b)'''.format(**locals())


month_regex = r'\b(jan(uary)?|feb(ruary)?|mar(ch)?|apr(il)?|may|jun(e)?|jul(y)?|aug(ust)?|sep(tember)?|oct(ober)?|nov(ember)?|dec(ember)?)\b'

# https://regex101.com/r/hP0qH4/6
# expansive_day_regex = r'''(
# # 12/5/16
# [0-1]?[0-9]\/[0-3]?[0-9]\/1\d
# |
# # 1st(of )?Jan
# (
#     ([ ]?on)?[ ]?{potential_ordinal}
#     ([ ]of[ ])?([ ]week[ ](in|of)?)?[ ]?
#     {month_regex}[ ]?
#     {potential_ordinal}[ ]?
# )
# # (next )?Monday
# |
# {days_with_optional_modifiers_before_and_after_regex}([ ]next[ ]week[ ]|[ ]in[ ])?
# # 3rd
# ([ ]?[0-3]?[0-9](th\b|st\b|nd\b|rd\b)?)?
# )'''.format(month_regex=month_regex, days_with_optional_modifiers_before_and_after_regex=days_with_optional_modifiers_before_and_after_regex, potential_ordinal=potential_ordinal)


ordinal_or_date_regex = r'({ordinal_regex}|{month_date})'.format(ordinal_regex=ordinal_regex, month_date=month_date)

expansive_day_regex = r'''
(∆
# Explicit date via combination
    # Mon 1st Jan | Mon Jan 1st
|   ((on|next([ ]week)?)[ ])?   ({day_regex}[ ])?(   ({ordinal_or_date_regex}[ ])((of)[ ])?{month_regex}
                                           |   ({month_regex}[ ]){ordinal_or_date_regex}   )
    # First Mon of Jan | 1st Week in Jan
|   ((on|next([ ]week)?)[ ])?   (first|second|third|fourth|following|coming|last)[ ](({day_regex}|Week)[ ])   ((in|of)[ ])?   {month_regex}



# Explicit dates by themselves
|   ((on|next([ ]week)?)[ ])?   (   {ordinal_or_date_regex}([ ]{month_regex})   |   ({month_regex}[ ]){ordinal_or_date_regex}   )
|   ((on|next([ ]week)?)[ ])?   {day_regex}
|   ((on|next([ ]week)?)[ ])?   [0-1]?[0-9]\/[0-3]?[0-9]\/1\d




)
# make all [ ]'s optional
# include next month in "Jan"
# Next week also mondifier for "Mon"
# Next (week)? Mon | Mon Next (week)?
# next week = next week | week after next | X weeks (time)?
'''.format(day_regex=day_regex, ordinal_or_date_regex=ordinal_or_date_regex, month_regex=month_regex)

time_regex = r'\b(1[0-9]|2[0-4]|0?[1-9]|00)[:.]?([0-5][0-9])?([ ]?am|pm)?\b'


def between_times(text):
    """between 5:30 - 7:30

    [description]

    Arguments:
        text {[type]} -- [description]

    Returns:
        [type] -- [description]
    """
    # TODO: Make this more liberal and then then have a stricter test in the custom replacement function
    # to ensure that one of the potential times is definitely a time
    between_times_regex = re.compile(r'(?P<first_time>(between|from)[ ]{potential_time_regex})[ ]?-[ ]?(?P<second_time>{potential_time_regex})'.format(potential_time_regex=potential_time_regex), re.IGNORECASE | re.VERBOSE)
    # between_times_regex = re.compile(r'(?P<before>between[ ]{potential_time_regex})[ ]?-[ ]?(?P<after>{potential_time_regex})'.format(well_formed_time_regex=well_formed_time_regex), re.IGNORECASE | re.VERBOSE)

    def custom_replacement(match):
        first_time = match.group('first_time')
        second_time = match.group('second_time')

        compiled_well_formed_time_regex = re.compile(well_formed_time_regex, re.IGNORECASE | re.VERBOSE)

        if not (re.search(compiled_well_formed_time_regex, first_time) or re.search(compiled_well_formed_time_regex, second_time)):
            return match.group()

        return first_time + ' - ' + second_time
    # custom_replacement = lambda m: m.group('before') + ' and ' + m.group('after')

    return re.sub(between_times_regex, custom_replacement, text)


def dash_between_two_times(text):
    '''
    e.g., 5-7pm
    '''
    dash_betweeen_two_times_regex = re.compile(r'(?P<first_time>1[0-9]|2[0-4]|0?[1-9]|00)(?P<dash>[ ]?-[ ]?)(?P<second_time>(?:1[0-9]|2[0-4]|0?[1-9]|00)[ ]?)(?P<ampm>am|pm)', re.IGNORECASE)

    def custom_replacement(match):
        ampm = match.group('ampm')
        ampm_to_add = ampm
        second_time = match.group('second_time')

        if match.group('second_time').strip().startswith('12'):
            # Assume they don't mean midnight
            # However, wit.ai thinks that 12pm = midnight and 12am = midday
            ampm = 'am'
            ampm_to_add = 'am'
            # print(second_time)
            # second_time = second_time if re.search(re.compile(r'(am|pm)', re.I), second_time) else '{}pm'.format(second_time)
        elif int(match.group('first_time')) > int(match.group('second_time')):
            # e.g., 11 > 5, therefore am instead of pm
            ampm_to_add = 'am' if ampm_to_add == 'pm' else 'pm'

        return match.group('first_time') + ampm_to_add + match.group('dash') + second_time + ampm


    return re.sub(dash_betweeen_two_times_regex, custom_replacement, text)


def multiple_times_on_same_day(text):
    '''
    e.g., 11 or 12 on Friday >> Friday at 11 or Friday at 12
    '''

    # multiple_times_regex = re.compile(r'(?P<first_time>{time_regex})(?P<or>[ ]?([ ]or[ ]|/|\\)[ ]?)(?P<second_time>{time_regex})(?P<day>[ ](on[ ]|next[ ]|this[ ]|(the[ ])?(first|second|third|fourth|following|coming|last)[ ])?{day_regex})'.format(time_regex=time_regex, day_regex=day_regex), re.IGNORECASE)
    multiple_times_regex = re.compile(r'(?P<first_time>{time_regex})(?P<or>[ ]?([ ]or[ ]|/|\\)[ ]?)(?P<second_time>{time_regex})[ ]?(?P<day>{day_regex})'.format(time_regex=time_regex, day_regex=expansive_day_regex), re.IGNORECASE | re.VERBOSE)

    def custom_replacement(match):
        format_time = lambda t: (match.group('day') + ' at ' + t).lstrip()

        return format_time(match.group('first_time')) + ' or ' + format_time(match.group('second_time'))


    return re.sub(multiple_times_regex, custom_replacement, text)


def same_time_on_multiple_days(text):
    """
    'Monday or Tuesday at 5pm'
    """
    custom_day_regex = r'{day_modifiers_regex}?{day_regex}'.format(day_modifiers_regex=day_modifiers_regex, day_regex=day_regex)

    multiple_times_regex = re.compile(r'(?P<first_day>{day_regex})(?P<or>[ ]?([ ]or[ ]|/|\\)[ ]?)(?P<second_day>{day_regex})[ ]?(at|@)[ ]?(?P<time>{time_regex})'.format(time_regex=time_regex, day_regex=custom_day_regex), re.IGNORECASE)


    def custom_replacement(match):
        format_time = lambda d: (match.group('time') + ' on ' + d).lstrip()

        return format_time(match.group('first_day')) + ' or ' + format_time(match.group('second_day'))


    return re.sub(multiple_times_regex, custom_replacement, text)


# def before_after_time_without_ampm(text):
#     '''
#     We add ':00' instead of am or pm because lots of times are ambiguous, e.g., 7 => 7am or 7pm?
#     '''
#     time_without_ampm_regex = re.compile(r'(before|after)[ ](?P<day>{days_with_modifiers_regex})'.format(days_with_modifiers_regex=days_with_modifiers_regex), re.IGNORECASE)
#     # print(time_without_ampm_regex.pattern)
#     custom_replacement = lambda m: m.group('hour') + ':00' + ' ' + m.group('day')

#     return re.sub(time_without_ampm_regex, custom_replacement, text)


def single_time_without_ampm(text):
    '''
    We add ':00' instead of am or pm because lots of times are ambiguous, e.g., 7 => 7am or 7pm?
    '''
    time_without_ampm_regex = re.compile(r'(?P<preamble>before[ ]|after[ ]|)?(?<![:\d])(?P<hour>(^|[^:.])\d\d?)[ ](?P<day>{days_with_modifiers_regex})'.format(days_with_modifiers_regex=days_with_modifiers_regex), re.IGNORECASE)

    # time_without_ampm_regex = re.compile(r'(?<![:\d])(?P<hour>(^|[^:.])\d\d?)[ ](?P<day>{days_with_modifiers_regex})'.format(days_with_modifiers_regex=days_with_modifiers_regex), re.IGNORECASE)
    # print(time_without_ampm_regex.pattern)
    custom_replacement = lambda m: m.group('preamble') + m.group('hour') + ':00' + ' ' + m.group('day')

    return re.sub(time_without_ampm_regex, custom_replacement, text)


def afternoon_on_day(text):
    """'afternoon on monday' => 'monday afternoon'

    TODO: Write unit tests for this
    TODO: What about 'afternoon next monday', etc.?

    Arguments:
        text {[type]} -- [description]

    Returns:
        [type] -- [description]
    """
    period_on_day_regex = re.compile(r'(?P<period>\b{named_time_period_regex}\b)(?P<on>[ ]on[ ])(?P<day>{day_regex})'.format(named_time_period_regex=named_time_period_regex, day_regex=day_regex), re.IGNORECASE)

    custom_replacement = lambda m: m.group('day') + ' ' + m.group('period')

    return re.sub(period_on_day_regex, custom_replacement, text)


def remove_confusing_words(text):
    """
    Removes 'sometime' or 'anytime' or 'just', these words do not add any necessary content and throw wit.ai off

    Arguments:
        text {[type]} -- [description]
    """

    # Removing this word results in an extra space, should we remove it?
    sometime_regex = re.compile(r'(some[ ]?time|any[ ]?time|\bjust\b)[ ]', re.IGNORECASE)

    return re.sub(sometime_regex, '', text)


def after_or_before_lone_number(text):
    """
    'Any time after 11 tomorrow'
    'Before 3 today'
    'After 1 on the 12th?'

    Arguments:
        text {[type]} -- [description]
    """
    regex = re.compile(after_or_before_lone_number_regex, re.I)

    def custom_replacement(match):
        new_hour_string = formatters.add_ampm_to_time_string(match.group('lone_number'))

        return match.group('after_before') + ' ' + new_hour_string + ' ' + match.group('day')


    return re.sub(regex, custom_replacement, text)


def time_onwards(text):
    """'from 10 o'clock onwards', etc

    Arguments:
        text {[type]} -- [description]

    Returns:
        [type] -- [description]
    """
    time_onwards_regex = re.compile(r'(from[ ])?(?P<time>{well_formed_time_regex})[ ]?onwards'.format(well_formed_time_regex=well_formed_time_regex), re.IGNORECASE | re.VERBOSE)

    custom_replacement = lambda m: 'after {}'.format(m.group('time'))

    return re.sub(time_onwards_regex, custom_replacement, text)


def until_time(text):
    """
    'Call me tomorrow morning until 11 UTC+2.''
    """

    regex = re.compile(r'(?P<day>{days_with_optional_modifiers_before_and_after_regex})[ ]?until[ ]?(?P<time>{time_regex})'.format(days_with_optional_modifiers_before_and_after_regex=days_with_optional_modifiers_before_and_after_regex, time_regex=time_regex), re.IGNORECASE)

    def custom_replacement(match):
        time = match.group('time')

        # If time doesn't have am or pm, include it
        if not re.search(re.compile(r'(am|pm)', re.I), time):
            time = formatters.add_ampm_to_time_string(time)

        return '{} before {}'.format(match.group('day'), time)


    return re.sub(regex, custom_replacement, text)


def lone_number_with_timezone(text):
    regex = re.compile(r'(?P<day>{day_regex}[ ]?{named_time_period_regex}?)[ ]?(?P<lone_number>{first_half_of_time_regex})[ ]?(?P<timezone>{all_timezones})'.format(day_regex=day_regex, named_time_period_regex=named_time_period_regex, first_half_of_time_regex=first_half_of_time_regex, all_timezones=timezones.all_timezone_types_regex), re.IGNORECASE)

    def custom_replacement(match):
        new_hour_string = formatters.add_ampm_to_time_string(match.group('lone_number'))

        return '{} {} {}'.format(match.group('day'), new_hour_string, match.group('timezone'))
        # return match.group('after_before') + ' ' + new_hour_string + ' ' + match.group('day') +


    return re.sub(regex, custom_replacement, text)


def dates_interval(text):
    """
    'from 4-7th July', 'from 4-7 July' => 'from 4th-7th July'
    """
    # regex_EXAMPLE = re.compile(r'(?P<day>{day_regex}[ ]?{named_time_period_regex}?)(?P<lone_number>{first_half_of_time_regex})[ ]?(?P<timezone>{all_timezones})'.format(day_regex=day_regex, named_time_period_regex=named_time_period_regex, first_half_of_time_regex=first_half_of_time_regex, all_timezones=timezones.all_timezone_types_regex), re.IGNORECASE)

    regex = re.compile(r'(?P<from>from[ ])?(?P<potential_ordinal_one>{potential_ordinal})[ ]?(-|to|till|until)[ ]?(?P<potential_ordinal_two>{potential_ordinal})[ ](?P<month>{month})'.format(potential_ordinal=potential_ordinal, month=month_regex), re.IGNORECASE)

    def custom_replacement(match):
        first_ordinal = match.group('potential_ordinal_one')
        second_ordinal = match.group('potential_ordinal_two')

        is_ordinal = lambda s: bool(re.search(re.compile(r'(st|nd|rd|th)', re.I), s))

        # TODO: Should we include this test?  Is it too restrictive?
        # Ensure these are dates
        if not match.group('from') and not (is_ordinal(first_ordinal) or is_ordinal(second_ordinal)):
            # Return unchanged
            return match.group()

        def get_ordinal(potential_ordinal_string):
            just_numbers = int(re.sub(r'\D', '', potential_ordinal_string))

            return formatters.get_ordinal_from_number(just_numbers)

        return 'from {date_one} {month} - {date_two} {month}'.format(date_one=get_ordinal(first_ordinal), date_two=get_ordinal(second_ordinal), month=match.group('month'))


    return re.sub(regex, custom_replacement, text)


def fix_twelve(text):
    """
    wit.ai doesn't get 12 very well


    Include 'pm' onto every definite mention of twelve

    Arguments:
        text {[type]} -- [description]

    Returns:
        [type] -- [description]
    """

    regex = r'(?P<time>12:[0-5][0-9])([ ]?am)?(?![ ]?pm)'

    custom_replacement = lambda m: '{}pm'.format(m.group('time'))

    return re.sub(regex, custom_replacement, text)


def preprocess_string_for_wit(text):
    '''
    wit.ai struggles with certain things, we can assist it with preprocessing steps to remove ambiguities
    '''
    preprocessed = text

    # Note: Order is important
    functions_to_run = [
        remove_confusing_words,
        dash_between_two_times,
        multiple_times_on_same_day,
        same_time_on_multiple_days,
        single_time_without_ampm,
        afternoon_on_day,
        between_times,
        after_or_before_lone_number,
        time_onwards,
        until_time,
        lone_number_with_timezone,
        dates_interval,
        fix_twelve,
    ]

    for func in functions_to_run:
        preprocessed = func(preprocessed)

    return preprocessed
