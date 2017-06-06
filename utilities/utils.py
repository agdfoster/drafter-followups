'''
Utilities module
'''

import re
import enum
import datetime
import time
import random
import operator
import sys
import itertools

import pytz
import arrow
# import cld2
import dateutil.parser
import segtok.segmenter


def ceil_dt(date, delta):
    """Round datetime up to the nearest delta"""
    return date + (datetime.datetime.min - date) % delta


def datetime_to_timestamp(date):
    return arrow.get(date).timestamp


def is_contained_within(potential_child, potential_parent):
    if isinstance(potential_child, tuple):
        subrange_start, subrange_end = potential_child
    else:
        subrange_start = subrange_end = potential_child

    parent_start, parent_end = potential_parent

    is_wholly_contained = subrange_start >= parent_start and parent_end >= subrange_end

    # print('is_contained_within: {} | {}: {}'.format(potential_child, potential_parent, is_wholly_contained))

    return is_wholly_contained


def choose_best_slots(slots, number_of_slots_to_choose, user_timezone, slot_size=datetime.timedelta(minutes=30)):
    """
    Note: This function prefers 10-12 and 14:30-17:00

    Note: We assume all slots are 30 mins
    """
    if not slots:
        return []


    if any(not isinstance(slot, tuple) for slot in slots):
        raise ValueError('Not all elements were tuples: {}'.format(slots))


    if contains_overlap(slots):
        raise ValueError('Slots contain overlap')

    if slot_size != datetime.timedelta(minutes=30):
        number_of_consecutive_slots = slot_size.seconds / datetime.timedelta(minutes=30).seconds

        # print('number_of_consecutive_slots: {}'.format(number_of_consecutive_slots))
        # print('slots before reformatting: {}'.format(slots))

        # Throw error if not a multiple of 30 mins
        if number_of_consecutive_slots % 1 != 0:
            raise ValueError('Slot size was not a multiple of 30 mins')

        number_of_consecutive_slots = int(number_of_consecutive_slots)

        # Ensure slots are sorted
        slots = sorted(slots, key=operator.itemgetter(0))
        # Check that all slots start exactly at the end of their predecessors
        # Note that index is the enumeration is not the actual position in the list, just the position in the enumeration (and thus starts from 0)
        # end_of_previous_slot = slots[index][1]
        are_slots_adjacent = lambda slots: all(start == slots[index][1] for index, (start, _) in enumerate(slots[1:]))

        adjacent_slots = []
        i = 0
        # for i, _ in enumerate(slots[:-1]):
        while i < len(slots) - 1:
            next_slots = slots[i:i + number_of_consecutive_slots]
            # print('next_slots: {}'.format(next_slots))

            if len(next_slots) < number_of_consecutive_slots:
                # It is impossible to find the correct size slot now
                break

            # does it have number_of_consecutive_slots (including itself)
            if next_slots and are_slots_adjacent(next_slots):
                # if yes, add to bucket and remove (number_of_consecutive_slots - 1) from list

                # Change the adjacent slots into one single slot
                new_start, _ = next_slots[0]
                _, new_end = next_slots[-1]
                adjacent_slots += [(new_start, new_end)]

                # Skip the adjacent slots - this ensures we never propose overlapping times
                i += number_of_consecutive_slots - 1

            i += 1

        slots = adjacent_slots
        # print('Slots after reformatting in choose_best_slots: {}'.format(slots))


    chosen_slots = []

    if contains_overlap(slots):
        raise ValueError('Slots contain overlap')

    # def morning_sort(slot):
    #     start, _ = slot
    #     date = epoch_timestamp_to_datetime(start, timezone=user_timezone)

    #     return abs(date.hour - 10)

    # def afternoon_sort(slot):
    #     start, _ = slot
    #     date = epoch_timestamp_to_datetime(start, timezone=user_timezone)

    #     return abs(date.hour - 14)

    def is_on_the_hour(slot):
        start, _ = slot
        date = epoch_timestamp_to_datetime(start, timezone=user_timezone)

        return date.minute == 0

    def is_morning(slot):
        start, _ = slot
        date = epoch_timestamp_to_datetime(start, timezone=user_timezone)

        # Less than 12 to ensure the interval doesn't finish later than 12
        return 10 <= date.hour < 12


    def is_afternoon(slot):
        start, _ = slot
        date = epoch_timestamp_to_datetime(start, timezone=user_timezone)

        # Less than 17 to ensure the interval doesn't finish later than 17
        return 14 <= date.hour < 17


    # random.shuffle(slots)
    # randomly_chosen_slots = slots[:number_of_slots_to_choose]

    # randomly_chosen_slots.sort(key=operator.itemgetter(0))
    # return randomly_chosen_slots

    morning_slots = [slot for slot in slots if is_morning(slot)]
    morning_slots.sort(key=operator.itemgetter(0))

    # - if there are slots between 10-12 pick one
    chosen_slots += morning_slots[:1]
    # print('chosen_slots: {}'.format(chosen_slots))
    # print('all slots: {}'.format(slots))


    if number_of_slots_to_choose > len(chosen_slots):
        afternoon_slots = [slot for slot in slots if is_afternoon(slot)]
        afternoon_slots.sort(key=operator.itemgetter(0))

        # - if there are slots between 14-17 pick one
        chosen_slots += afternoon_slots[:1]

        slots = list(set(slots) - set(chosen_slots))

        # - pick at random until on the hour until necessary number of slots is found
        # [Order remaining slots to be on the hour (randomly ordered) then off the hour (randomly ordered)]
        on_the_hour_slots = [slot for slot in slots if is_on_the_hour(slot)]
        random.shuffle(on_the_hour_slots)
        off_the_hour_slots = [slot for slot in slots if not is_on_the_hour(slot)]
        random.shuffle(off_the_hour_slots)

        extra_slots_to_choose_from = on_the_hour_slots + off_the_hour_slots

        def do_slots_overlap(slot1, slot2):
            start1, end1 = slot1
            start2, end2 = slot2

            overlap1 = end1 > start2 and end2 >= end1
            overlap2 = end2 > start1 and end1 >= end2

            return overlap1 or overlap2

        does_slot_overlap = lambda slot: any(do_slots_overlap(existing_slot, slot) for existing_slot in chosen_slots)
        # Remove any overlapping slots from extra_slots
        # TODO: This does not work at the moment
        # extra_slots_to_choose_from = [slot for slot in extra_slots_to_choose_from if not does_slot_overlap(slot)]

        extra_slots_to_get = number_of_slots_to_choose - len(chosen_slots)
        chosen_slots += extra_slots_to_choose_from[:extra_slots_to_get]


    # Old version
    # ===========
    # Get first slot (prioritise 10-12)
    # first_slot_prioritised = sorted(slots, key=morning_sort)
    # first_slot, *_ = first_slot_prioritised
    # chosen_slots += [first_slot]
    # slots.remove(first_slot)


    # # Get second slots (prioristise 14:30-17:00)
    # if number_of_slots_to_choose > 1:
    #     second_slot_prioritised = sorted(slots, key=afternoon_sort)

    #     second_slot, *_ = second_slot_prioritised
    #     chosen_slots += [second_slot]
    #     second_slot_prioritised.remove(second_slot)

    #     further_slots_prioritised = sorted(slots, key=is_on_the_hour)
    #     is_on_the_hour
    #     if number_of_slots_to_choose > 2:
    #         chosen_slots += further_slots_prioritised[:number_of_slots_to_choose - 2]

    # chosen_slots = random.sample(slots, number_of_slots_to_choose)


    # Sort by date
    chosen_slots.sort(key=operator.itemgetter(0))
    # print('chosen_slots: {}'.format(chosen_slots))
    # random.shuffle(chosen_slots)

    return chosen_slots


def get_slots_from_days(days, user_timezone, take_any_available=False):
    """
    Get two hour slots from the days

    Arguments:
        days {[type]} -- [description]
        user_timezone {[type]} -- [description]

    Returns:
        [type] -- [description]

    Raises:
        ValueError -- [description]
    """
    all_slots = list(itertools.chain(*days))

    # print('Inside get_slots_from_days with {}'.format(days))
    get_two_hour_slots = lambda intervals, num_slots: choose_best_slots(intervals, num_slots, user_timezone, slot_size=datetime.timedelta(hours=2))
    get_one_hour_slots = lambda intervals, num_slots: choose_best_slots(intervals, num_slots, user_timezone, slot_size=datetime.timedelta(hours=1))

    # Change (start, end) to list of 30 min chunks
    filtered_days = [chunk_timestamps(day) for day in days]
    # print('filtered_days: {}'.format(filtered_days))

    try:
        first_day = next(day for day in filtered_days if get_two_hour_slots(day, 2))

        potential_second_days = filtered_days[filtered_days.index(first_day)+1:]

        second_day = next(day for day in potential_second_days if get_two_hour_slots(day, 1))
    except StopIteration:
        # Maximise chance of finding slots
        # TODO: How do we test this? Create events in the calendar?
        return choose_best_slots(all_slots, 3, user_timezone)


    # print('first_day: {}'.format(first_day))
    # print('second_day: {}'.format(second_day))
    slots = get_two_hour_slots(first_day, 2) + get_two_hour_slots(second_day, 1)

    if len(slots) != 3:
        try:
            first_day = next(day for day in filtered_days if get_one_hour_slots(day, 2))

            potential_second_days = filtered_days[filtered_days.index(first_day)+1:]

            second_day = next(day for day in potential_second_days if get_one_hour_slots(day, 1))

            return get_one_hour_slots(first_day, 2) + get_one_hour_slots(second_day, 1)
        except StopIteration:
            # Maximise chance of finding slots
            # TODO: How do we test this? Create events in the calendar?
            return choose_best_slots(all_slots, 3, user_timezone)
        # raise ValueError('Could not find 3 slots')

    return slots


def group_slots_by(slots, func, reverse=False):
    sorted_days = sorted(slots, key=func, reverse=reverse)
    grouped_days = itertools.groupby(sorted_days, func)

    days = [list(values) for _, values in grouped_days]
    days = [day for day in days if day]

    return days


def contains_overlap(list_of_tups):
    """Returns boolean for whether the tuples contain any overlap, i.e., [(1, 3), (2, 4)] = True"""
    if not list_of_tups:
        return False


    # We assume that all tuples with be length 2
    sorted_tups = sorted(list_of_tups, key=operator.itemgetter(0))

    prev_tup, *_ = sorted_tups
    for tup in sorted_tups[1:]:
        if prev_tup[1] > tup[0]:
            return True

    return False


def get_best_slots_for_week(potential_meeting_slots, user_timezone):
    """
    Tuesday first, then Wed,Thur,Fri,Mon

    TODO: Change this
    - Get first day (Tuesday first, then Wed,Thur,Fri,Mon) which has 2 two-hour slots free
    - Then get the next day with one two-hour slot free
    - If not enough slots fall back to 30 mins

    Arguments:
        potential_meeting_slots {[type]} -- [description]
        user_timezone {[type]} -- [description]

    Raises:
        ValueError -- [description]
    """
    get_weekday = lambda slot: epoch_timestamp_to_datetime(slot[0], timezone=user_timezone).weekday()

    # (Tuesday first, then Wed, Thur, Fri, Mon)
    best_days_dic = {
        0: 5,
        1: 1,
        2: 2,
        3: 3,
        4: 4,
        5: 100,
        6: 100
        }
    best_days = lambda slot: best_days_dic[get_weekday(slot)]

    # hours_in_working_day = 9
    # days = choose_best_slots(potential_meeting_slots, sys.maxsize, user_timezone, slot_size=datetime.timedelta(hours=hours_in_working_day))

    # # We assume that these slots do not stretch over 2 days
    # get_day = lambda window: arrow.get(epoch_timestamp_to_datetime(window[0], timezone=user_timezone).date()).timestamp


    grouped_days = group_slots_by(potential_meeting_slots, best_days)
    # groupby assumes sorted data
    # TODO: Refactor this to make it more readable
    # grouped_days = list(dict(itertools.groupby(sorted(potential_meeting_slots, key=best_days), best_days)).values())


    # sorted_days = sorted(filtered_slots, key=best_days)
    # grouped_days = itertools.groupby(sorted_days, best_days)

    # days = [list(values) for _, values in grouped_days]
    # days = [day for day in days if day]


    # # [(key, values)] - sort by key
    # grouped_days.sort(key=lambda tup: best_days((tup[0], 0)))


    # # [(key, >groupby iterator>)]
    # days = [list(tup[1]) for tup in grouped_days]

    # days = [day for day in days if day]

    # days.sort(key=best_days)

    # print('grouped_days: {}'.format(grouped_days))

    slots_from_days = get_slots_from_days(grouped_days, user_timezone)

    if contains_overlap(slots_from_days):
        raise ValueError('Slots contain overlap')

    return slots_from_days


def get_best_slots_for_month(potential_meeting_slots, user_timezone):
    """
    Get first whole business day after the 3rd

    TODO: Should we include a parameter for how many days to find?
    If so, how should we space out the days?


    TODO: Change this
    - Get first date (after 3rd) which has 2 two-hour slots free
    - Then get the next date with one two-hour slot free
    - If not enough slots fall back to 30 mins
    """
    get_day = lambda slot: epoch_timestamp_to_datetime(slot[0], timezone=user_timezone).day


    hours_in_working_day = 9
    days = choose_best_slots(potential_meeting_slots, sys.maxsize, user_timezone, slot_size=datetime.timedelta(hours=hours_in_working_day))
    # sort_by_day
    # grouped_by_day = itertools.groupby(potential_meeting_slots, get_day)


    filtered_days = [day for day in days if get_day(day) > 2]

    # print('filtered_days: {}'.format(filtered_days))


    return get_slots_from_days(filtered_days, user_timezone)


def epoch_timestamp_to_datetime(epoch_timestamp, timezone=None):
    # Python datetimes are always relative to the local time (and not UTC)
    tzinfo = None
    if timezone:
        if isinstance(timezone, (pytz.tzinfo.StaticTzInfo, pytz.tzinfo.DstTzInfo)) or timezone == pytz.UTC:
            # print('timezone: {}'.format(timezone))
            tzinfo = timezone
        elif isinstance(timezone, str):
            tzinfo = pytz.timezone(timezone)
        else:
            tzinfo = pytz.timezone(timezone.timezone_string)

        # tzinfo = pytz.timezone(timezone) if isinstance(timezone, str) else pytz.timezone(timezone.timezone_string)

    date = datetime.datetime.fromtimestamp(epoch_timestamp, tzinfo)


    return date


def is_today(dt, reference_time=None):
    today = reference_time.date() if reference_time else datetime.datetime.now().date()

    if isinstance(dt, tuple):
        # print('is tuple')
        # print(dt)
        # Remove one minute for intervals that end with the day (and therefore on the first minute of another day)
        return dt[0].date() == (dt[1] - datetime.timedelta(minutes=1)).date() == today


    return dt.date() == today and not is_not_this_year(dt)


# TODO: Make these timezone aware
def is_tomorrow(dt, reference_time=None):
    tomorrow = reference_time.date() if reference_time else datetime.datetime.now().date()
    tomorrow += datetime.timedelta(days=1)

    if isinstance(dt, tuple):
        start, end = dt
        # print('is tuple')
        # print(dt)
        # Remove one minute for intervals that end with the day (and therefore on the first minute of another day)
        return start.date() == (end - datetime.timedelta(minutes=1)).date() == tomorrow and not is_not_this_year(dt)


    return dt.date() == tomorrow and not is_not_this_year(dt)
    # return dt.date() == datetime.datetime.now().date() + datetime.timedelta(days=1)


def is_after_next_week(dt):
    # What about the last few weeks of the year?
    now = datetime.datetime.now()

    return dt.isocalendar()[1] > now.isocalendar()[1] + 1 or not is_not_this_year(dt)


def is_not_this_month(dt):
    return dt.month > datetime.datetime.now().month or not is_not_this_year(dt)


def is_not_this_year(dt):
    return dt.year != datetime.datetime.now().year


def remove_timezone(dt):
    return dt.replace(tzinfo=None)


def same_day_timestamps(first, second, timezone=None):
    get_time = lambda time: time[0] if isinstance(time, tuple) else time

    first_date = epoch_timestamp_to_datetime(get_time(first), timezone=timezone)
    second_date = epoch_timestamp_to_datetime(get_time(second), timezone=timezone)

    return same_day(first_date, second_date)


def same_day(first, second):
    return first.date() == second.date()


def is_next_occurrence_of_day(date):
    """Is this date the very next occurrence of the day of week?, i.e., next wednesday"""
    if is_today(date):
        return True

    if not (is_this_week(date) or is_next_week(date)):
        return False

    # This can be done slightly more elegantly
    if is_this_week(date):
        return datetime.datetime.now().weekday() < date.weekday()
    else: # utils.is_next_week(dt)
        return datetime.datetime.now().weekday() > date.weekday()


def is_next_week(dt):
    # Last week of the year
    return dt.isocalendar()[1] == datetime.datetime.now().isocalendar()[1] + 1


def is_this_week(dt, reference_time=None):
    this_week = reference_time.isocalendar()[1] if reference_time else datetime.datetime.now().isocalendar()[1]

    if isinstance(dt, tuple):
        return dt[0].isocalendar()[1] == dt[1].isocalendar()[1] == this_week


    return dt.isocalendar()[1] == this_week


def get_sentences_plain(text):
    return list(segtok.segmenter.split_multi(text))


def get_sentences(text):
    """Only split if greater than 256 chars (max length for wit.ai)

    Arguments:
        text {[type]} -- [description]

    Returns:
        [type] -- [description]
    """
    sentences_to_return = []
    sentences = list(segtok.segmenter.split_multi(text))

    current_string = sentences.pop()

    while len(current_string) < 256 and len(sentences) != 0:
        current_string = sentences.pop() + ' ' + current_string

        if len(current_string) > 256:
            sentences_to_return += [current_string]
            current_string = ''

    sentences_to_return += [current_string]

    # Remove duplicates
    return list(set(sentences_to_return))


def convert_date_string_to_date(date_string, timezone_string):
    timezone = pytz.timezone(timezone_string)

    parsed_date = dateutil.parser.parse(date_string)
    localised_date = timezone.localize(parsed_date)

    return timezone.localize(parsed_date, is_dst=bool(localised_date.dst()))


def get_first_name(name):
    """Returns the first name for a given name"""
    match = re.search(r'^\w+', name)

    return match.group() if match else ''


def timestamp_in_past(timestamp, reference_timestamp=None):
    now_timestamp = reference_timestamp or int(time.time())

    timestamp = timestamp[1] if isinstance(timestamp, tuple) else timestamp

    return now_timestamp > timestamp


def is_in_daytime_hours(date):
    """ 0700 - 2300 """
    return datetime.time(7) <= date.time() <= datetime.time(23)


def is_in_working_hours(date):
    '''
    This should only be for fixing obvious errors (i.e., 2:30am vs 2:30pm) and should mostly defer to wit.ai
    '''
    return datetime.time(9) <= date.time() <= datetime.time(18)


def in_past(time, reference_time=None):
    '''
    Accepts datetime instance or tuple where first element is datetime instance
    '''
    # timezone = pytz.timezone(timezone) if isinstance(timezone, str) else timezone
    now = reference_time if reference_time else datetime.datetime.now()

    # Greater than or equal to because wit.ai will classify 'now' et al. as this very instant
    if isinstance(time, tuple):
        # Time window
        return now >= time[1]
    elif isinstance(time, datetime.datetime):
        # Single time
        return now >= time
    else:
        raise ValueError('time had invalid type "{}"'.format(type(time)))


@enum.unique
class Granularity(enum.Enum):
    specific = 1
    hour = 2
    hour_window = 3
    day = 4
    week = 5
    month = 6


def get_granularity(window):
    '''
    If someone says 'anytime after 3', that is probably a small window, technically it is 3-12
    but business hours are not until midnight
    '''

    if not isinstance(window, tuple):
        return Granularity.specific

    start, end = window
    # print('inside get_granularity with: {}'.format(window))
    window_size = end - start


    if window_size == datetime.timedelta(hours=24).total_seconds():
        return Granularity.day
    elif window_size == datetime.timedelta(hours=1).total_seconds():
        return Granularity.specific
    elif window_size >= datetime.timedelta(days=8).total_seconds():
        return Granularity.month
    elif window_size > datetime.timedelta(days=1).total_seconds():
        return Granularity.week
    # wit.ai's morning/afternoon sizes are > 6 hours, 4-12 and 12-7
    elif window_size >= datetime.timedelta(hours=6).total_seconds():
        return Granularity.hour_window
    else:
        return Granularity.hour


def detect_language(text):
    raise ValueError('TODO')
    # _, _, details = cld2.detect(text)

    # top_choice, *_ = details

    # lang = top_choice[1]

    # return lang


def is_timestamp_in_daytime(timestamp, timezone=None):
    date = epoch_timestamp_to_datetime(timestamp, timezone=timezone)

    return is_in_daytime_hours(date)


def is_timestamp_in_working_hours(timestamp, timezone=None):
    date = epoch_timestamp_to_datetime(timestamp, timezone=timezone)

    return is_in_working_hours(date)


def is_slot_in_daytime(slot, timezone=None):
    start, end = slot

    return is_timestamp_in_daytime(start, timezone=timezone) and is_timestamp_in_daytime(end, timezone=timezone)


def is_slot_in_working_hours(slot, timezone=None):
    start, end = slot

    return is_timestamp_in_working_hours(start, timezone=timezone) and is_timestamp_in_working_hours(end, timezone=timezone)


def chunk_timestamp(timestamps, meeting_length=datetime.timedelta(minutes=30)):
    meeting_length_in_seconds = meeting_length.seconds

    if isinstance(timestamps, (float, int)):
        interval = timestamps

        return [(interval, interval + meeting_length_in_seconds)]
    else:
        # print('timestamps: {}'.format(timestamps))
        start, end = timestamps

        if end - start == meeting_length_in_seconds:
            return timestamps

        return list(zip(range(int(start), int(end) - meeting_length_in_seconds, meeting_length_in_seconds), range(int(start) + meeting_length_in_seconds, int(end), meeting_length_in_seconds)))


def chunk_timestamps(timestamps, meeting_length=datetime.timedelta(minutes=30)):
    if isinstance(timestamps, list):
        return [chunk_timestamp(timestamp, meeting_length=meeting_length) for timestamp in timestamps]
    else:
        return chunk_timestamp(timestamps, meeting_length=meeting_length)
