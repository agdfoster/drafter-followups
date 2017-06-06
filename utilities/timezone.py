"""
A class representing a timezone in text
"""

import re
import logging
import datetime

import pytz

from . import timezones

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

handler = logging.StreamHandler()
logger.addHandler(handler)


TIMEZONES_TO_UPPERCASE_REGEX = re.compile(r'\b(PS?T|GMT|ET|BST|UTC|ACDT|ACST|ACT|ACT|ADT|AEDT|AEST|AFT|AKDT|AKST|AMST|AMT|AMT|ART|AST|AST|AWDT|AWST|AZOST|AZT|BDT|BDT|BIOT|BRST|BRT|BST|BST|BST|BTT|CCT|CDT|CDT|CEDT|CEST|CET|CHADT|CHAST|CHOT|ChST|CHUT|CIST|CIT|CKT|CLST|CLT|COT|CST|CST|CST|CST|CST|CT|CVT|CWST|CXT|DAVT|DDUT|DFT|EASST|ECT|ECT|EDT|EEDT|EEST|EET|EGST|EGT|EIT|EST|EST|FET|FJT|FKST|FKST|FKT|FNT|GALT|GAMT|GFT|GILT|GIT|GMT|GST|GST|GYT|HADT|HAEC|HAST|HKT|HMT|HOVT|HST|IBST|ICT|IDT|IRDT|IRKT|IRST|IST|IST|IST|JST|KGT|KOST|KRAT|KST|LHST|LHST|LINT|MAGT|MART|MAWT|MDT|MET|MEST|MHT|MIST|MMT|MSK|MST|MST|MST|MUT|MVT|MYT|NCT|NDT|NFT|NPT|NST|NT|NUT|NZDT|NZST|OMST|ORAT|PDT|PETT|PGT|PHOT|PKT|PMDT|PMST|PONT|PST|PST|PYST|PYT|RET|ROTT|SAKT|SAMT|SAST|SBT|SCT|SGT|SLST|SRET|SRT|SST|SST|SYOT|TAHT|THA|TFT|TJT|TKT|TLT|TMT|TOT|TVT|ULAT|USZ1|UYST|UYT|UZT|VET|VLAT|VOLT|VOST|VUT|WAKT|WAST|WAT|WEDT|WEST|WET|WST|YAKT)\b', re.IGNORECASE)

class TimeZone():
    """
    This represents the timezone of an email

    TODO: Add the functions that find timezones in strings to this class
    """

    def __init__(self, exact_string):
        if not exact_string:
            raise ValueError('No string provided')

        self.exact_string = exact_string
        logger.debug('Inside TimeZone constructor with "{}"'.format(exact_string))

        formatted_string = exact_string

        if re.search(TIMEZONES_TO_UPPERCASE_REGEX, exact_string.strip()):
            formatted_string = exact_string.strip().upper()

        self.formatted_string = formatted_string


        self.timezone_string = timezones.get_timezone_from_natural_lang(exact_string)

        if not self.timezone_string:
            if exact_string in pytz.common_timezones_set:
                # i.e., not a string a human would say
                self.timezone_string = exact_string
                self.formatted_string = pytz.timezone(exact_string).localize(datetime.datetime.now(), is_dst=None).tzname()


    @staticmethod
    def create_timezone(exact_string):
        """This is the way to create a timezone

        Arguments:
            exact_string {[type]} -- [description]

        Returns:
            [type] -- [description]
        """

        timezone = TimeZone(exact_string)

        if not timezone.is_valid():
            return None

        return timezone


    def is_valid(self):
        return bool(self.timezone_string)


    def __str__(self):
        return self.formatted_string


    def get_pytz(self):
        return pytz.timezone(self.timezone_string)
