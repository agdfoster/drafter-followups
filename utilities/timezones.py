"""
This module is a helper for timezones
"""

import re
import logging

import pytz
import datetime


logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

handler = logging.StreamHandler()
logger.addHandler(handler)


timezone_regex = r'\b((GMT|UTC)([ ]?((\+|-)\d\d?:?\d?\d?))?|PS?T|∆USA|∆US|ET|BST|∆UK|UK[ ]?[Tt]ime|[Ee]astern [Tt]ime|[Pp]acific [Tt]ime|[Cc]entral [Tt]ime|∆UTC|ACDT|ACST|ACT|ACT|ADT|AEDT|AEST|AFT|AKDT|AKST|AMST|AMT|AMT|ART|AST|AST|AWDT|AWST|AZOST|AZT|BDT|BDT|BIOT|BRST|BRT|BST|BST|BST|BTT|CCT|CDT|CDT|CEDT|CEST|CET|CHADT|CHAST|CHOT|ChST|CHUT|CIST|CIT|CKT|CLST|CLT|COT|CST|CST|CST|CST|CST|CT|CVT|CWST|CXT|DAVT|DDUT|DFT|EASST|ECT|ECT|EDT|EEDT|EEST|EET|EGST|EGT|EIT|EST|EST|FET|FJT|FKST|FKST|FKT|FNT|GALT|GAMT|GFT|GILT|GIT|GMT|GST|GST|GYT|HADT|HAEC|HAST|HKT|HMT|HOVT|HST|IBST|ICT|IDT|IRDT|IRKT|IRST|IST|JST|KGT|KOST|KRAT|KST|LHST|LHST|LINT|MAGT|MART|MAWT|MDT|MET|MEST|MHT|MIST|MMT|MSK|MST|MST|MST|MUT|MVT|MYT|NCT|NDT|NFT|NPT|NST|NT|NUT|NZDT|NZST|OMST|ORAT|PDT|PETT|PGT|PHOT|PKT|PMDT|PMST|PONT|PST|PST|PYST|PYT|RET|ROTT|SAKT|SAMT|SAST|SBT|SCT|SGT|SLST|SRET|SRT|SST|SST|SYOT|TAHT|THA|TFT|TJT|TKT|TLT|TMT|TOT|TVT|ULAT|USZ1|UYST|UYT|UZT|VET|VLAT|VOLT|VOST|VUT|WAKT|WAST|WAT|WEDT|WEST|WET|WST|YAKT)\b'

# place_time_regex = r'\b(Abidjan|Accra|Addis[ ]Ababa|Algiers|Asmara|Asmera|Bamako|Bangui|Banjul|Bissau|Blantyre|Brazzaville|Bujumbura|Cairo|Casablanca|Ceuta|Conakry|Dakar|Dar[ ]es[ ]Salaam|Djibouti|Douala|El[ ]Aaiun|Freetown|Gaborone|Harare|Johannesburg|Juba|Kampala|Khartoum|Kigali|Kinshasa|Lagos|Libreville|Lome|Luanda|Lubumbashi|Lusaka|Malabo|Maputo|Maseru|Mbabane|Mogadishu|Monrovia|Nairobi|Ndjamena|Niamey|Nouakchott|Ouagadougou|Porto-Novo|Sao[ ]Tome|Timbuktu|Tripoli|Tunis|Windhoek|Adak|Anchorage|Anguilla|Antigua|Araguaina|Buenos[ ]Aires|Catamarca|ComodRivadavia|Cordoba|Jujuy|La[ ]Rioja|Mendoza|Rio[ ]Gallegos|Salta|San[ ]Juan|San[ ]Luis|Tucuman|Ushuaia|Aruba|Asuncion|Atikokan|Atka|Bahia|Bahia[ ]Banderas|Barbados|Belem|Belize|Blanc-Sablon|Boa[ ]Vista|Bogota|Boise|Buenos[ ]Aires|Cambridge[ ]Bay|Campo[ ]Grande|Cancun|Caracas|Catamarca|Cayenne|Cayman|Chicago|Chihuahua|Coral[ ]Harbour|Cordoba|Costa[ ]Rica|Creston|Cuiaba|Curacao|Danmarkshavn|Dawson|Dawson[ ]Creek|Denver|Detroit|Dominica|Edmonton|Eirunepe|El[ ]Salvador|Ensenada|Fort[ ]Nelson|Fort[ ]Wayne|Fortaleza|Glace[ ]|Godthab|Goose[ ]|Grand[ ]Turk|Grenada|Guadeloupe|Guatemala|Guayaquil|Guyana|Halifax|Havana|Hermosillo|Indiana/Indianapolis|Indiana/Knox|Indiana/Marengo|Indiana/Petersburg|Indiana/Tell[ ]City|Indiana/Vevay|Indiana/Vincennes|Indiana/Winamac|Indianapolis|Inuvik|Iqaluit|Jamaica|Jujuy|Juneau|Kentucky/Louisville|Kentucky/Monticello|Knox[ ]IN|Kralendijk|La[ ]Paz|Lima|Los[ ]Angeles|Louisville|Lower[ ]Princes|Maceio|Managua|Manaus|Marigot|Martinique|Matamoros|Mazatlan|Mendoza|Menominee|Merida|Metlakatla|Mexico[ ]City|Miquelon|Moncton|Monterrey|Montevideo|Montreal|Montserrat|Nassau|New[ ]York|Nipigon|Nome|Noronha|North[ ]Dakota/Beulah|North[ ]Dakota/Center|North[ ]Dakota/New[ ]Salem|Ojinaga|Panama|Pangnirtung|Paramaribo|Phoenix|Port[ ]of[ ]Spain|Port-au-Prince|Porto[ ]Acre|Porto[ ]Velho|Puerto[ ]Rico|Rainy[ ]River|Rankin[ ]Inlet|Recife|Regina|Resolute|Rio[ ]Branco|Rosario|Santa[ ]Isabel|Santarem|Santiago|Santo[ ]Domingo|Sao[ ]Paulo|Scoresbysund|Shiprock|Sitka|St[ ]Barthelemy|St[ ]Johns|St[ ]Kitts|St[ ]Lucia|St[ ]Thomas|St[ ]Vincent|Swift[ ]Current|Tegucigalpa|Thule|Thunder[ ]Bay|Tijuana|Toronto|Tortola|Vancouver|Virgin|Whitehorse|Winnipeg|Yakutat|Yellowknife|Casey|Davis|DumontDUrville|Macquarie|Mawson|McMurdo|Palmer|Rothera|South[ ]Pole|Syowa|Troll|Vostok|Longyearbyen|Aden|Almaty|Amman|Anadyr|Aqtau|Aqtobe|Ashgabat|Ashkhabad|Baghdad|Bahrain|Baku|Bangkok|Barnaul|Beirut|Bishkek|Brunei|Calcutta|Chita|Choibalsan|Chongqing|Chungking|Colombo|Dacca|Damascus|Dhaka|Dili|Dubai|Dushanbe|Gaza|Harbin|Hebron|Ho[ ]Chi[ ]Minh|Hong[ ]Kong|Hovd|Irkutsk|Istanbul|Jakarta|Jayapura|Jerusalem|Kabul|Kamchatka|Karachi|Kashgar|Kathmandu|Katmandu|Khandyga|Kolkata|Krasnoyarsk|Kuala Lumpur|Kuching|Kuwait|Macao|Macau|Magadan|Makassar|Manila|Muscat|Nicosia|Novokuznetsk|Novosibirsk|Omsk|Oral|Phnom Penh|Pontianak|Pyongyang|Qatar|Qyzylorda|Rangoon|Riyadh|Saigon|Sakhalin|Samarkand|Seoul|Shanghai|Singapore|Srednekolymsk|Taipei|Tashkent|Tbilisi|Tehran|Tel[ ]Aviv|Thimbu|Thimphu|Tokyo|Tomsk|Ujung[ ]Pandang|Ulaanbaatar|Ulan[ ]Bator|Urumqi|Ust-Nera|Vientiane|Vladivostok|Yakutsk|Yekaterinburg|Yerevan|Azores|Bermuda|Canary|Cape[ ]Verde|Faeroe|Faroe|Jan[ ]Mayen|Madeira|Reykjavik|South[ ]Georgia|St[ ]Helena|Stanley|Adelaide|Brisbane|Broken[ ]Hill|Canberra|Currie|Darwin|Eucla|Hobart|Lindeman|Lord[ ]Howe|Melbourne|Perth|Queensland|Sydney|Tasmania|Victoria|Yancowinna|Acre|DeNoronha|Atlantic|Central|East-Saskatchewan|Newfoundland|Saskatchewan|Yukon|Continental|EasterIsland|CST6CDT|Cuba|Egypt|Eire|Greenwich|Universal|Zulu|Amsterdam|Andorra|Astrakhan|Athens|Belfast|Belgrade|Berlin|Bratislava|Brussels|Bucharest|Budapest|Busingen|Chisinau|Copenhagen|Dublin|Gibraltar|Guernsey|Helsinki|Isle[ ]of[ ]Man|Istanbul|Jersey|Kaliningrad|Kiev|Kirov|Lisbon|Ljubljana|London|Luxembourg|Madrid|Malta|Mariehamn|Minsk|Monaco|Moscow|Nicosia|Oslo|Paris|Podgorica|Prague|Riga|Rome|Samara|San[ ]Marino|Sarajevo|Simferopol|Skopje|Sofia|Stockholm|Tallinn|Tirane|Tiraspol|Ulyanovsk|Uzhgorod|Vaduz|Vatican|Vienna|Vilnius|Volgograd|Warsaw|Zagreb|Zaporozhye|Zurich|Greenwich|Hongkong|Iceland|Antananarivo|Chagos|Christmas|Cocos|Comoro|Kerguelen|Mahe|Maldives|Mauritius|Mayotte|Reunion|Iran|Israel|Jamaica|Japan|Kwajalein|Libya|BajaNorte|BajaSur|Navajo|NZ|NZ-CHAT|Apia|Auckland|Bougainville|Chatham|Chuuk|Easter|Efate|Enderbury|Fakaofo|Fiji|Funafuti|Galapagos|Gambier|Guadalcanal|Honolulu|Johnston|Kiritimati|Kosrae|Kwajalein|Majuro|Marquesas|Midway|Nauru|Niue|Norfolk|Noumea|Pago Pago|Palau|Pitcairn|Pohnpei|Ponape|Port[ ]Moresby|Rarotonga|Saipan|Samoa|Tahiti|Tarawa|Tongatapu|Wake|Wallis|Yap|Poland|Portugal|Singapore|Turkey|Alaska|Aleutian|Arizona|East-Indiana|Hawaii|Indiana-Starke|Michigan|Pacific-New|Samoa|Zulu)[ ]?[tT]ime'

#TODO: country_time_regex/lookup


# This will get all city timezones

timezones = pytz.common_timezones_set - {'UTC', 'GMT'}

get_city = lambda tz: tz.split('/')[-1].replace('_', ' ')

CITY_TIMEZONE_LOOKUP = {get_city(tz): tz for tz in timezones}

# nationality_time_regex = r'\b(Spanish|English|Scottish|Irish|Welsh|French|German|Italian|Belgian)[ ]?[tT]ime'


NATIONALITY_TIMEZONE_LOOKUP = {
    'Spanish': 'Europe/Paris',
    'French': 'Europe/Paris',
    'German': 'Europe/Paris',
    'Italian': 'Europe/Paris',
    'Belgian': 'Europe/Paris',
    'English': 'Europe/London',
    'Scottish': 'Europe/London',
    'Irish': 'Europe/London',
    'Welsh': 'Europe/London',
    'UK': 'Europe/London',
    'Israel': 'Israel',
}

def create_regex_from_tz_dict(dic):
    values = [v.replace(' ', '[ ]') for v in dic.keys()]

    return r'\b(' + '|'.join(values) + r')[ ]time?'

# create_regex_from_tz_dict = lambda dic: r'\b(' + '|'.join(d.keys()) + r')[ ]time?'

nationality_time_regex = create_regex_from_tz_dict(NATIONALITY_TIMEZONE_LOOKUP)
place_time_regex = create_regex_from_tz_dict(CITY_TIMEZONE_LOOKUP)

all_timezone_types_regex = r'({timezone_regex}|{place_time_regex}|{nationality_time_regex})'.format(**locals())

# TIMEZONE_LOOKUP = {pytz.timezone(x).localize(datetime.datetime.now()).tzname(): x for x in pytz.all_timezones}

# When people say GMT+1/UTC+1, they really mean outside daylight savings, need to account for daylight savings
# We should create a lookup table for different ways to say the same timezone, e.g., Eastern time = ET = EDT = East coast time
# TIMEZONE_LOOKUP = {
#     '+03': 'Europe/Kirov',
#     '+04': 'Europe/Ulyanovsk',
#     '+05': 'Asia/Oral',
#     '+06': 'Asia/Qyzylorda',
#     '+07': 'Asia/Tomsk',
#     'ACST': 'Australia/Yancowinna',
#     'ACT': 'Brazil/Acre',
#     'ACWST': 'Australia/Eucla',
#     'ADT': 'Canada/Atlantic',
#     'AEST': 'Australia/Victoria',
#     'AFT': 'Asia/Kabul',
#     'AKDT': 'US/Alaska',
#     'AMT': 'Brazil/West',
#     'ANAT': 'Asia/Anadyr',
#     'ART': 'America/Rosario',
#     'AST': 'Asia/Riyadh',
#     'AWST': 'Australia/West',
#     'AZOST': 'Atlantic/Azores',
#     'AZT': 'Asia/Baku',
#     'BDT': 'Asia/Dhaka',
#     'BNT': 'Asia/Brunei',
#     'BOT': 'America/La_Paz',
#     'BRT': 'Brazil/East',
#     'BST': 'Europe/London',
#     'BTT': 'Asia/Thimphu',
#     'CAT': 'Africa/Maputo',
#     'CCT': 'Indian/Cocos',
#     'CDT': 'US/Indiana-Starke',
#     'CT': 'US/Indiana-Starke',
#     'CEST': 'Poland',
#     'CET': 'Europe/Paris',
#     'CHAST': 'Pacific/Chatham',
#     'CHOST': 'Asia/Choibalsan',
#     'CHUT': 'Pacific/Yap',
#     'CKT': 'Pacific/Rarotonga',
#     'CLT': 'Chile/Continental',
#     'COT': 'America/Bogota',
#     'CST': 'ROC',
#     'CVT': 'Atlantic/Cape_Verde',
#     'CXT': 'Indian/Christmas',
#     'ChST': 'Pacific/Saipan',
#     'DAVT': 'Antarctica/Davis',
#     'DDUT': 'Antarctica/DumontDUrville',
#     'EAST': 'Pacific/Easter',
#     'EAT': 'Indian/Mayotte',
#     'ECT': 'America/Guayaquil',
#     'EDT': 'US/Michigan',
#     'EEST': 'Turkey',
#     'EET': 'Libya',
#     'EGST': 'America/Scoresbysund',
#     'EST': 'America/New_York',
#     'ET': 'America/New_York',
#     'FJT': 'Pacific/Fiji',
#     'FKST': 'Atlantic/Stanley',
#     'FNT': 'Brazil/DeNoronha',
#     'GALT': 'Pacific/Galapagos',
#     'GAMT': 'Pacific/Gambier',
#     'GET': 'Asia/Tbilisi',
#     'GFT': 'America/Cayenne',
#     'GILT': 'Pacific/Tarawa',
#     'GMT': 'Europe/London',
#     'GMT+1': 'Etc/GMT+1',
#     'GMT+10': 'Etc/GMT+10',
#     'GMT+11': 'Etc/GMT+11',
#     'GMT+12': 'Etc/GMT+12',
#     'GMT+2': 'Etc/GMT+2',
#     'GMT+3': 'Etc/GMT+3',
#     'GMT+4': 'Etc/GMT+4',
#     'GMT+5': 'Etc/GMT+5',
#     'GMT+6': 'Etc/GMT+6',
#     'GMT+7': 'Etc/GMT+7',
#     'GMT+8': 'Etc/GMT+8',
#     'GMT+9': 'Etc/GMT+9',
#     'GMT-1': 'Etc/GMT-1',
#     'GMT-10': 'Etc/GMT-10',
#     'GMT-11': 'Etc/GMT-11',
#     'GMT-12': 'Etc/GMT-12',
#     'GMT-13': 'Etc/GMT-13',
#     'GMT-14': 'Etc/GMT-14',
#     'GMT-2': 'Etc/GMT-2',
#     'GMT-3': 'Etc/GMT-3',
#     'GMT-4': 'Etc/GMT-4',
#     'GMT-5': 'Etc/GMT-5',
#     'GMT-6': 'Etc/GMT-6',
#     'GMT-7': 'Etc/GMT-7',
#     'GMT-8': 'Etc/GMT-8',
#     'GMT-9': 'Etc/GMT-9',
#     'GST': 'Atlantic/South_Georgia',
#     'GYT': 'America/Guyana',
#     'HDT': 'US/Aleutian',
#     'HKT': 'Hongkong',
#     'HOVST': 'Asia/Hovd',
#     'HST': 'US/Hawaii',
#     'ICT': 'Asia/Vientiane',
#     'IDT': 'Israel',
#     'IOT': 'Indian/Chagos',
#     'IRDT': 'Iran',
#     'IRKT': 'Asia/Irkutsk',
#     'IST': 'Israel',
#     'JST': 'Japan',
#     'KGT': 'Asia/Bishkek',
#     'KOST': 'Pacific/Kosrae',
#     'KRAT': 'Asia/Novokuznetsk',
#     'KST': 'ROK',
#     'LHST': 'Australia/Lord_Howe',
#     'LINT': 'Pacific/Kiritimati',
#     'MAGT': 'Asia/Magadan',
#     'MART': 'Pacific/Marquesas',
#     'MAWT': 'Antarctica/Mawson',
#     'MDT': 'US/Mountain',
#     'MEST': 'MET',
#     'MHT': 'Pacific/Majuro',
#     'MIST': 'Antarctica/Macquarie',
#     'MMT': 'Asia/Rangoon',
#     'MSK': 'W-SU',
#     'MST': 'US/Arizona',
#     'MUT': 'Indian/Mauritius',
#     'MVT': 'Indian/Maldives',
#     'MYT': 'Asia/Kuching',
#     'NCT': 'Pacific/Noumea',
#     'NDT': 'Canada/Newfoundland',
#     'NFT': 'Pacific/Norfolk',
#     'NOVT': 'Asia/Novosibirsk',
#     'NPT': 'Asia/Katmandu',
#     'NRT': 'Pacific/Nauru',
#     'NUT': 'Pacific/Niue',
#     'NZST': 'Pacific/Auckland',
#     'OMST': 'Asia/Omsk',
#     'PDT': 'US/Pacific-New',
#     'PT': 'US/Pacific-New',
#     'PET': 'America/Lima',
#     'PETT': 'Asia/Kamchatka',
#     'PGT': 'Pacific/Port_Moresby',
#     'PHOT': 'Pacific/Enderbury',
#     'PHT': 'Asia/Manila',
#     'PKT': 'Asia/Karachi',
#     'PMDT': 'America/Miquelon',
#     'PONT': 'Pacific/Ponape',
#     # Not Pacific/Pitcairn
#     'PST': 'America/Los_Angeles',
#     'PWT': 'Pacific/Palau',
#     'PYT': 'America/Asuncion',
#     'RET': 'Indian/Reunion',
#     'ROTT': 'Antarctica/Rothera',
#     'SAKT': 'Asia/Sakhalin',
#     'SAMT': 'Europe/Samara',
#     'SAST': 'Africa/Mbabane',
#     'SBT': 'Pacific/Guadalcanal',
#     'SCT': 'Indian/Mahe',
#     'SGT': 'Singapore',
#     'SRET': 'Asia/Srednekolymsk',
#     'SRT': 'America/Paramaribo',
#     'SST': 'US/Samoa',
#     'SYOT': 'Antarctica/Syowa',
#     'TAHT': 'Pacific/Tahiti',
#     'TFT': 'Indian/Kerguelen',
#     'TJT': 'Asia/Dushanbe',
#     'TKT': 'Pacific/Fakaofo',
#     'TLT': 'Asia/Dili',
#     'TMT': 'Asia/Ashkhabad',
#     'TOT': 'Pacific/Tongatapu',
#     'TVT': 'Pacific/Funafuti',
#     'UCT': 'UCT',
#     'ULAST': 'Asia/Ulan_Bator',
#     'UTC': 'Zulu',
#     'UYT': 'America/Montevideo',
#     'UZT': 'Asia/Tashkent',
#     'VET': 'America/Caracas',
#     'VLAT': 'Asia/Vladivostok',
#     'VOST': 'Antarctica/Vostok',
#     'VUT': 'Pacific/Efate',
#     'WAKT': 'Pacific/Wake',
#     'WAT': 'Africa/Windhoek',
#     'WEST': 'WET',
#     'WET': 'Africa/El_Aaiun',
#     'WFT': 'Pacific/Wallis',
#     'WGST': 'America/Godthab',
#     'WIB': 'Asia/Pontianak',
#     'WIT': 'Asia/Jayapura',
#     'WITA': 'Asia/Ujung_Pandang',
#     'WSST': 'Pacific/Apia',
#     'XJT': 'Asia/Urumqi',
#     'YAKT': 'Asia/Yakutsk',
#     'YEKT': 'Asia/Yekaterinburg'
# }


ABBR_LOOKUP = {
    '+03': 'Europe/Kirov',
    '+04': 'Europe/Ulyanovsk',
    '+05': 'Asia/Oral',
    '+06': 'Asia/Qyzylorda',
    '+07': 'Asia/Tomsk',
    'ACST': 'Australia/Yancowinna',
    'ACT': 'Brazil/Acre',
    'ACWST': 'Australia/Eucla',
    'ADT': 'Canada/Atlantic',
    'AEST': 'Australia/Victoria',
    'AFT': 'Asia/Kabul',
    'AKDT': 'US/Alaska',
    'AMT': 'Brazil/West',
    'ANAT': 'Asia/Anadyr',
    'ART': 'America/Rosario',
    'AST': 'Asia/Riyadh',
    'AWST': 'Australia/West',
    'AZOST': 'Atlantic/Azores',
    'AZT': 'Asia/Baku',
    'BDT': 'Asia/Dhaka',
    'BNT': 'Asia/Brunei',
    'BOT': 'America/La_Paz',
    'BRT': 'Brazil/East',
    'BST': 'Europe/London',
    'BTT': 'Asia/Thimphu',
    'CAT': 'Africa/Maputo',
    'CCT': 'Indian/Cocos',
    'CEST': 'Poland',
    'CET': 'Europe/Paris',
    'CHAST': 'Pacific/Chatham',
    'CHOST': 'Asia/Choibalsan',
    'CHUT': 'Pacific/Yap',
    'CKT': 'Pacific/Rarotonga',
    'CLT': 'Chile/Continental',
    'COT': 'America/Bogota',
    'CST': 'America/Chicago',
    'CDT': 'America/Chicago',
    'CT': 'America/Chicago',
    'CVT': 'Atlantic/Cape_Verde',
    'CXT': 'Indian/Christmas',
    'ChST': 'Pacific/Saipan',
    'DAVT': 'Antarctica/Davis',
    'DDUT': 'Antarctica/DumontDUrville',
    'EAST': 'Pacific/Easter',
    'EAT': 'Indian/Mayotte',
    'ECT': 'America/Guayaquil',
    'EEST': 'Turkey',
    'EET': 'Libya',
    'EGST': 'America/Scoresbysund',
    'EDT': 'America/New_York',
    'EST': 'America/New_York',
    'ET': 'America/New_York',
    'FJT': 'Pacific/Fiji',
    'FKST': 'Atlantic/Stanley',
    'FNT': 'Brazil/DeNoronha',
    'GALT': 'Pacific/Galapagos',
    'GAMT': 'Pacific/Gambier',
    'GET': 'Asia/Tbilisi',
    'GFT': 'America/Cayenne',
    'GILT': 'Pacific/Tarawa',
    'GMT+1': 'Etc/GMT+1',
    'GMT+10': 'Etc/GMT+10',
    'GMT+11': 'Etc/GMT+11',
    'GMT+12': 'Etc/GMT+12',
    'GMT+2': 'Etc/GMT+2',
    'GMT+3': 'Etc/GMT+3',
    'GMT+4': 'Etc/GMT+4',
    'GMT+5': 'Etc/GMT+5',
    'GMT+5:30': 'Asia/Kolkata',
    'UTC+5:30': 'Asia/Kolkata',
    'GMT+6': 'Etc/GMT+6',
    'GMT+7': 'Etc/GMT+7',
    'GMT+8': 'Etc/GMT+8',
    'GMT+9': 'Etc/GMT+9',
    'GMT-1': 'Etc/GMT-1',
    'GMT-10': 'Etc/GMT-10',
    'GMT-11': 'Etc/GMT-11',
    'GMT-12': 'Etc/GMT-12',
    'GMT-13': 'Etc/GMT-13',
    'GMT-14': 'Etc/GMT-14',
    'GMT-2': 'Etc/GMT-2',
    'GMT-3': 'Etc/GMT-3',
    'GMT-4': 'Etc/GMT-4',
    'GMT-5': 'Etc/GMT-5',
    'GMT-6': 'Etc/GMT-6',
    'GMT-7': 'Etc/GMT-7',
    'GMT-8': 'Etc/GMT-8',
    'GMT-9': 'Etc/GMT-9',
    # Put this at the end so the regex doesn't match it first
    'GMT': 'Europe/London',
    'GST': 'Atlantic/South_Georgia',
    'GYT': 'America/Guyana',
    'HDT': 'US/Aleutian',
    'HKT': 'Hongkong',
    'HOVST': 'Asia/Hovd',
    'HST': 'US/Hawaii',
    'ICT': 'Asia/Vientiane',
    'IDT': 'Israel',
    'IOT': 'Indian/Chagos',
    'IRDT': 'Iran',
    'IRKT': 'Asia/Irkutsk',
    'IST': 'Israel',
    'JST': 'Japan',
    'KGT': 'Asia/Bishkek',
    'KOST': 'Pacific/Kosrae',
    'KRAT': 'Asia/Novokuznetsk',
    'KST': 'ROK',
    'LHST': 'Australia/Lord_Howe',
    'LINT': 'Pacific/Kiritimati',
    'MAGT': 'Asia/Magadan',
    'MART': 'Pacific/Marquesas',
    'MAWT': 'Antarctica/Mawson',
    'MT': 'US/Mountain',
    'MST': 'US/Mountain',
    'MDT': 'US/Mountain',
    'MEST': 'MET',
    'MHT': 'Pacific/Majuro',
    'MIST': 'Antarctica/Macquarie',
    'MMT': 'Asia/Rangoon',
    'MSK': 'W-SU',
    'MUT': 'Indian/Mauritius',
    'MVT': 'Indian/Maldives',
    'MYT': 'Asia/Kuching',
    'NCT': 'Pacific/Noumea',
    'NDT': 'Canada/Newfoundland',
    'NFT': 'Pacific/Norfolk',
    'NOVT': 'Asia/Novosibirsk',
    'NPT': 'Asia/Katmandu',
    'NRT': 'Pacific/Nauru',
    'NUT': 'Pacific/Niue',
    'NZST': 'Pacific/Auckland',
    'OMST': 'Asia/Omsk',
    # Not Pacific/Pitcairn
    'PDT': 'America/Los_Angeles',
    'PT': 'America/Los_Angeles',
    'PST': 'America/Los_Angeles',
    'PET': 'America/Lima',
    'PETT': 'Asia/Kamchatka',
    'PGT': 'Pacific/Port_Moresby',
    'PHOT': 'Pacific/Enderbury',
    'PHT': 'Asia/Manila',
    'PKT': 'Asia/Karachi',
    'PMDT': 'America/Miquelon',
    'PONT': 'Pacific/Ponape',
    'PWT': 'Pacific/Palau',
    'PYT': 'America/Asuncion',
    'RET': 'Indian/Reunion',
    'ROTT': 'Antarctica/Rothera',
    'SAKT': 'Asia/Sakhalin',
    'SAMT': 'Europe/Samara',
    'SAST': 'Africa/Mbabane',
    'SBT': 'Pacific/Guadalcanal',
    'SCT': 'Indian/Mahe',
    'SGT': 'Singapore',
    'SRET': 'Asia/Srednekolymsk',
    'SRT': 'America/Paramaribo',
    'SST': 'US/Samoa',
    'SYOT': 'Antarctica/Syowa',
    'TAHT': 'Pacific/Tahiti',
    'TFT': 'Indian/Kerguelen',
    'TJT': 'Asia/Dushanbe',
    'TKT': 'Pacific/Fakaofo',
    'TLT': 'Asia/Dili',
    'TMT': 'Asia/Ashkhabad',
    'TOT': 'Pacific/Tongatapu',
    'TVT': 'Pacific/Funafuti',
    'UCT': 'UCT',
    'ULAST': 'Asia/Ulan_Bator',
    'UTC': 'Zulu',
    'UYT': 'America/Montevideo',
    'UZT': 'Asia/Tashkent',
    'VET': 'America/Caracas',
    'VLAT': 'Asia/Vladivostok',
    'VOST': 'Antarctica/Vostok',
    'VUT': 'Pacific/Efate',
    'WAKT': 'Pacific/Wake',
    'WAT': 'Africa/Windhoek',
    'WEST': 'WET',
    'WET': 'Africa/El_Aaiun',
    'WFT': 'Pacific/Wallis',
    'WGST': 'America/Godthab',
    'WIB': 'Asia/Pontianak',
    'WIT': 'Asia/Jayapura',
    'WITA': 'Asia/Ujung_Pandang',
    'WSST': 'Pacific/Apia',
    'XJT': 'Asia/Urumqi',
    'YAKT': 'Asia/Yakutsk',
    'YEKT': 'Asia/Yekaterinburg',
}


# TODO: Add all countries
COUNTRY_TIMEZONE_LOOKUP = {
    'Israel': 'Israel',
}
# a_lower = {k.upper():v for k,v in a.items()}


def lookup_in_tz_dictionaries(natural_language_timezone):
    ending_in_time_regex = re.compile(r'[ ]?TIME$')
    formatted_timezone = natural_language_timezone.strip().upper()
    formatted_timezone = re.sub(ending_in_time_regex, '', formatted_timezone)

    uppercase_dict_keys = lambda dic: {k.upper(): v for k, v in dic.items()}

    timezone = uppercase_dict_keys(ABBR_LOOKUP).get(formatted_timezone) or uppercase_dict_keys(CITY_TIMEZONE_LOOKUP).get(formatted_timezone) or uppercase_dict_keys(NATIONALITY_TIMEZONE_LOOKUP).get(formatted_timezone)

    return timezone


def get_timezone_from_natural_lang(natural_language_timezone):
    """Returns timezone info from a string specifying a timezone in natural language

    1. abbreviation, e.g., 'GMT'
    2. place name time, e.g., London time, UK time, Spanish time
    3. offset, e.g., 'GMT+3'

    Arguments:
        natural_language_timezone {[type]} -- [description]

    Returns:
        String -- timezone_string (pytz) or None if we couldn't figure it out
    """

    timezone = lookup_in_tz_dictionaries(natural_language_timezone)

    logger.debug('Inside get_timezone_from_natural_lang.  "%s" => "%s"', natural_language_timezone, timezone)

    if timezone:
        return timezone

    # get_utc_offset = lambda tz: datetime.datetime.now(pytz.timezone(tz)).strftime('%z')

    # if timezone:
    #     return get_utc_offset(timezone), formatted_timezone

    return None

# UK  NA
# GMT
# US  NA
# ∆UTC
# PT
# ET
# UK Time BST
# UKTime  BST
# UK time BST
# UKtime  BST
# Eastern Time    EST
# Eastern time    EST
# eastern time    EST
# eastern time    EST
# Pacific Time    PST
# Pacific time    PST
# pacific time    PST
# pacific time    PST
# Central Time    CT
# Central time    CT
# central time    CT
# central time    CT
# EasternTime EST
# Easterntime EST
# easterntime EST
# easterntime EST
# PacificTime PST
# Pacifictime PST
# pacifictime PST
# pacifictime PST
# CentralTime CT
# Centraltime CT
# centraltime CT
# centraltime CT

TZ_ABBR_TO_STRING = {

}


# pytz.timezone(pytz.common_timezones[103]).tzname(datetime.datetime.now())
