'''
Formatters for dates


TODO:
    - the Timezone class should have an instance method to offset a datetime
    - we should be passing Datetime classes to these formatting methods
    - is_tomorrow et al. should be instance methods of datetime entities or in the utilities module


Notes:
    - all formatting methods take a unix timestamp
'''

import re
import datetime

from ..utilities import utils


def add_ampm_to_time_string(time_string):
    hour = int(time_string)

    ampm = 'am' if 8 < hour < 12 else 'pm'
    new_hour_string = str(hour) + ampm

    return new_hour_string


def get_ordinal_from_number(num):
    if not isinstance(num, int):
        raise ValueError('{} is not an integer'.format(num))

    # TODO: Refactor to make this more readable
    return str(num) + ('th' if 11 <= num <= 13 else {1:'st', 2:'nd', 3:'rd'}.get(num % 10, 'th'))


def get_ordinal_day(date):
    '''
    Returns 1st, 2nd, 3rd, 18th, 19th, 22nd, etc.
    '''
    return get_ordinal_from_number(date.day)


def format_day(dt):
    if utils.is_today(dt):
        day = 'today'
    elif utils.is_tomorrow(dt):
        day = 'tomorrow'
    elif (utils.is_this_week(dt) or utils.is_next_week(dt)) and utils.is_next_occurrence_of_day(dt):
        day = 'on {dt:%A}'.format(dt=dt)
    elif utils.is_next_week(dt):
        day = 'next {dt:%A}'.format(dt=dt)
    else:
        day = 'on {dt:%A}'.format(dt=dt)

        if utils.is_after_next_week(dt):
            # include date
            day += ' ' + get_ordinal_day(dt)

            if utils.is_not_this_month(dt):
                # include month
                # if month has a short name, use whole month, else use 3 letter short form
                month_format_string = ' {dt:%B}' if 3 <= dt.month <= 7 else ' {dt:%b}'

                day += month_format_string.format(dt=dt)

                if utils.is_not_this_year(dt):
                    day += ' {dt:%Y}'.format(dt=dt)

    return day


def format_day_solo(date):
    """Format the day for display alone, as opposed to with a time"""
    return re.sub('on[ ]', '', format_day(date))


def format_time(epoch_timestamp, include_day=False, timezone=None, display_timezone=False):
    date = utils.epoch_timestamp_to_datetime(epoch_timestamp, timezone=timezone)

    # print('formatting {} with timezone "{}"'.format(epoch_timestamp, timezone))

    if not date:
        raise ValueError('Not a unix timestamp: "{}"'.format(epoch_timestamp))

    format_string = '{d:%I}{d:%p}' if date.minute == 0 else '{d:%I}:{d:%M}{d:%p}'
    time_formatted = format_string.format(d=date).lstrip('0').lower()

    if include_day:
        time_formatted += ' ' + format_day(date)

    if display_timezone:
        time_formatted += ' ({})'.format(timezone.formatted_string)

    return time_formatted


def format_time_window(window, include_day=True, timezone=None, display_timezone=False):
    '''
    Assumes start and end are in the same day

    9-12    Morning
    10-12   Morning after 10am
    9-11    Morning 9 - 11am
    same for afternoon
    '''
    from_time, to_time = window

    start_date = utils.epoch_timestamp_to_datetime(from_time, timezone=timezone)
    end_date = utils.epoch_timestamp_to_datetime(to_time, timezone=timezone)

    afternoon_start_hour = 14

    window_string = None

    if start_date.minute == 0 and end_date.minute == 0:
        formatted_day = format_day(start_date) if include_day else 'the'

        if start_date.hour == 9 and end_date.hour == 12:
            window_string = '{} morning'.format(formatted_day)
        elif start_date.hour == 10 and end_date.hour == 12:
            window_string = '{} morning after 10am'.format(formatted_day)
        elif start_date.hour == 9 and end_date.hour == 11:
            window_string = '{} morning 9 - 11am'.format(formatted_day)
        elif start_date.hour == afternoon_start_hour and end_date.hour == 18:
            window_string = '{} afternoon'.format(formatted_day)
        elif start_date.hour > 11 and end_date.hour == 18:
            formatted_hour = start_date.hour if start_date.hour < 13 else start_date.hour - 12

            if formatted_day == 'the':
                formatted_day = 'that'

            window_string = '{} afternoon after {}'.format(formatted_day, formatted_hour)

    if not window_string:
        window_string = 'between {} and {}'.format(format_time(from_time, timezone=timezone), format_time(to_time, include_day=include_day, timezone=timezone))

    return_string = 'anytime {window_string}'.format(window_string=window_string)

    # If its not really a window then format simply
    if to_time - from_time <= datetime.timedelta(hours=1).total_seconds():
        # Not really an interval
        return_string = format_time(from_time, include_day=include_day, timezone=timezone)


    if display_timezone:
        return_string += ' ({})'.format(timezone.formatted_string)

    return return_string


def get_time_format_func(time):
    return format_time_window if isinstance(time, tuple) else format_time


def get_two_slots_as_string(slots, answer_to_question=False, timezone=None, display_timezone=False):
    first, second = slots

    same_day = utils.same_day_timestamps(first, second, timezone=timezone)
    # start = ('Sure' if answer_to_question else 'Great') + ', '
    # 'Sure' was more trouble than it was worth
    start = ''

    formatted_first = get_time_format_func(first)(first, timezone=timezone, display_timezone=False, include_day=False if same_day else True)
    formatted_second = get_time_format_func(second)(second, include_day=True, timezone=timezone, display_timezone=display_timezone)

    return_string = start + 'I could do {} or {}'.format(formatted_first, formatted_second)

    # if display_timezone:
    #     return_string += ' ({})'.format(timezone.formatted_string)

    return return_string


def get_slots_as_string(slots, timezone=None, display_timezone=False):
    '''
    "Humanise" time slots.  Slots can be individual times or windows

    Note: at the moment it must be three slots, the last of which may be a time window
    e.g, 'Could you do Xpm on DAY, I could also do 5pm, otherwise anytime DAY+1 morning|afternoon|evening'

    TODO: This should take an arbitrary number of slots and format them well
    '''
    if len(slots) < 3:
        raise ValueError('Expects 3 slots, got "{}"'.format(slots))


    # print('inside get_slots_as_string with {}'.format(slots))

    first_time, second_time, third_time = slots

    if isinstance(third_time, tuple):
        start, end = third_time

        if end - start <= datetime.timedelta(hours=1).total_seconds():
            # Not really an interval
            third_time = start


    same_day = utils.same_day_timestamps(first_time, second_time, timezone=timezone)
    first_time_string = get_time_format_func(first_time)(first_time, include_day=True, timezone=timezone, display_timezone=display_timezone)
    second_time_string = get_time_format_func(second_time)(second_time, timezone=timezone, include_day=not same_day)

    third_time_string = get_time_format_func(third_time)(third_time, include_day=True, timezone=timezone)

    # third_time_string = format_time_window(third_time, include_day=True, timezone=timezone) if isinstance(third_time, tuple) else format_time(third_time, include_day=True, timezone=timezone)

    return 'Could you do {}? I could also do {}.\n\nOtherwise {}?'.format(first_time_string, second_time_string, third_time_string)


def single_slot_to_string(slot_choice, include_day=False, timezone=None, display_timezone=False):
    return format_time(slot_choice[0], include_day=include_day, timezone=timezone, display_timezone=display_timezone)


def single_slot_to_sentence(slot_choice, timezone=None, display_timezone=False):
    return 'Sure, ' + single_slot_to_string(slot_choice, include_day=True, timezone=timezone, display_timezone=display_timezone) + " works for me. I'll send a calendar invite.\n\nLooking forward to speaking."


def format_two_or_three_times_into_sentence(times, timezone=None, display_timezone=False):
    """
    Takes two or three times and creates a sentence from them

    Note: The times can be intervals or standalone times
    Note: The times can be on the same day or different days
    """
    if not 1 < len(times) < 4:
        raise ValueError('Wrong number of times')

    if len(times) == 2:
        return get_two_slots_as_string(times, timezone=timezone, display_timezone=display_timezone)
    else:
        return get_slots_as_string(times, timezone=timezone, display_timezone=display_timezone)
