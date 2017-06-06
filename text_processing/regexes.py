"""
This file is a home for all the regexes required by the module
"""

# import re
import regex as re

MARKDOWN_REGEX = r'\\([\\\`\*Is this}\[\]\(\)#\+-\.!])'


TIME_PERIOD_REGEX = re.compile(r'(year|month|\bweek\b|\bday)', re.IGNORECASE)
TIME_PERIOD_2_REGEX = re.compile(r'(afternoon|morning|morn\b|evening|eve\b|midday|weekend)', re.IGNORECASE)
MONTH_REGEX = re.compile(r'(january|jan\b|february|feb\b|march|mar\b|april|apr\b|may\b|june|jun\b|july|jul\b|august|aug\b|september|sept?|october|oct\b|november|nov\b|december|dec\b)', re.IGNORECASE)
DAY_REGEX = re.compile(r'(monday|mon\b|tuesday|tue\b|wednesday|weds?|thursday|thur|friday|fri\b|saturday|sat\b|sunday|sun\b)', re.IGNORECASE)
NUMERIC_TIME_REGEX = re.compile(r'(?:(\b|[^\d \.\:\-,]))((((1[0-9]|2[0-4]|0?[1-9]))(    )?((((\s?[\:\. ]\s?)([0-6][0-9])))(     )?|(\s?(pm|am|o\'?\s?clock)))( ?am| ?pm)?))', re.IGNORECASE)
RELATIVE_TIME_REGEX = re.compile(r'(next week|next month)', re.IGNORECASE)
FIRSTSECONDTHIRD_REGEX = re.compile(r'(1[0-9]th|[2-3]0th|[2-3]?1st|2?2nd|2?3rd|2?[4-9]th)', re.IGNORECASE)


CURRENCY_REGEX = r'(([ ]?([$£]|gbp|gpb|usd?|pounds?|dollars?|grande?)[ ]?){1,4}([ ]?[\d,-.]+[ ]?[kmbn]{1,2}|[ ]?[\d,-.]+)|([ ]?[\d,-.]+[ ]?[kmbn]{1,2}|[ ]?[\d,-.]+)[ ]?(([$£]|gbp|gpb|usd?|pounds?|dollars?|grande?)[ ]?){1,4})'

# TODO: Used to be 2 or more chevrons at start of line.  1 or more is quite broad
CHEVRON_REGEX = re.compile(r'(^>{1,}|>{3,}) ', re.MULTILINE)
LINES_WITHOUT_WORDS_REGEX = re.compile(r'(^|\r|\n)[ \|\W]+\b', re.MULTILINE)



# https://regex101.com/r/nF0qR6/
RE_SIGNATURE_IMPROVED = re.compile(r"""(
        ^
        (
            ;\):\)
            |:\-\)
            |:\)
            |all([ ]the)?[ ]best([ ]-)?
            |a[ ]smiling[ ]face[ ]is[ ]miles[ ]more[ ]attractive[ ]than[ ]just[ ]a[ ]pretty[ ]one
            |at[ ]your[ ]service
            |bests
            |best([ ]wishes)?
            |best[ ]regards[ ](and|&)[ ]good[ ]luck
            |be[ ]well
            |blessings
            |cheers
            |ciao
            |enthusiastically
            |god[ ]bless
            |have[ ]a[ ](wonderful|bountiful|blessed|lustful|nice)[ ]day
            |high[ ]five[ ]from[ ]down[ ]low
            |hope[ ]this[ ]helps
            |hope[ ]you[ ]have[ ]a[ ]great[ ]time
            |hugs
            |in[ ]haste
            |keep[ ]in[ ]touch
            |let[ ]me[ ]know[ ]if[ ]you[ ]need[ ]anything[ ]else
            |looking[ ]forward
            |(lots[ ]of[ ])?love
            |(i[ ])?(love|luv)[ ](you|ya)([ ][xo]+)?
            |love[ ][xo]+
            |make[ ]it[ ]a[ ]great[ ]day
            |(many[ ])?thanks([ ]so[ ]much|[ ]again)?
            |much[ ]appreciated
            |my[ ]best([ ]to[ ]you)?
            |now[ ]go[ ]do[ ]that[ ]voodoo[ ]that[ ]you[ ]do[ ]so[ ]well
            |peace
            |peace[ ]and[ ]love
            |peace[ ]dude
            |(regards|rgds)
            |respectfully
            |rushing
            |see[ ]you[ ]around
            |signed
            |sincerely([ ]yours)?
            |smile\![ ]\-[ ]it[ ]exercises[ ]the[ ]maximum[ ]facial[ ]muscles
            |smiley[ ]face
            |snuggles
            |speak[ ]soon
            |speak[ ]to[ ]you[ ]tomorrow
            |stay[ ]gold
            |take care
            |take[ ]care
            |take[ ]it[ ]easy[ ]bro
            |talk[ ](soon|later)
            |ta[ ]-?ta
            |thanking[ ]you[ ]in[ ]anticipation
            |thanks[ ]for[ ]your[ ]consideration
            |thanks[ ]much
            |thanks[ ](&|and)[ ]regards
            |thank[ ]you([ ](for[ ]your[ ]patronage|in[ ]advance))?
            |the[ ]purpose[ ]of[ ]education[ ]is[ ]not[ ]knowledge[ ]but[ ]right[ ]action
            |thx
            |till[ ]next[ ]time
            |to[ ]your[ ]success
            |ttfn
            |ttys
            |typos[ ]courtesy[ ]of[ ]my[ ]iphone
            |very[ ]truly[ ]yours
            |V\/R
            |waiting[ ]to[ ]hear[ ]your[ ]reply,[ ]with[ ]best[ ]regards
            |warmest
            |warmly
            |we[ ]look[ ]forward[ ]to[ ]seeing[ ]you
            |with[ ]appreciation
            |(with[ ])?(warm(est)?|kind(est)?|best(est)?)[ ]?regards
            |[xo]+
            |xoxo
            |you're[ ]the[ ]best
            |your[ ]servant[ ]in[ ]christ
            |yours([ ]truly)?
        )
        \s*
        (
            [.,;!-]+\s*|(\r?\n)+
        )
        .*\s*
    )""", re.IGNORECASE | re.MULTILINE | re.VERBOSE)


# https://regex101.com/r/tC7tC2
NAME_BASED_SIGNOFF_REGEX = r'(^[- ]{0,3}(%s)[ \S]*$)'

STANDARD_SIGNATURE_REGEX = r'^.*(^-{2,}$|^_{2,}$|^[^\d\w*\s]{3,300}$|begin forwarded message|sent from mobile|from my (iphone|ipad|mobile).?$|^\||sent (using|via) blackberry)[\w\W\s]*'

PIPE_BASE_SIGNATURE_REGEX = r'^.*(\|)[\w\W\s]*'


# https://regex101.com/r/zD4wN9
GREETING_REGEX = r'''(
      ^(%s)\S{0,3}
    |
      ^(
        all,
        |aloha
        |ciao
        |dear(est)?
        |g'?day
        |good[ ](day|morning|afternoon|evening|night)
        |greetings
        |guys,
        |h[eai]+y?a?
        |he?ii?
        |hello
        |hola
        |howdy
        |team
        |yo,
      )
      ((?![\n\r])[\W]?\S+){0,3}
    )
    [ ,]{0,10}$'''


# https://regex101.com/r/zH6yG6
BROAD_SIGNOFF_REGEX = re.compile(r'^(^-{2,}[ ]*$|^—+[ ]*$|^_{2,}[ ]*$|^[^\d\w*\s]{3,300}$|Begin forwarded message|from my (iPhone|iPad).?$|^\||Sent using BlackBerry|sent on the move)[\w\W\s]', re.IGNORECASE | re.MULTILINE)
EVERYTHING_AFTER_PIPE_REGEX = re.compile(r'^.*(\|)[\w\W\s]*', re.IGNORECASE | re.MULTILINE)

# See https://regex101.com/r/fS8lW9
NOREPLY_EMAIL_ADDRESS = re.compile(r'''(
        account
        |admin
        |alerts
        |billing
        |confirmation
        |customer(\b|.?care)
        |daemon
        |dev(\b|eloper)
        |email
        |help
        |info
        |invitations
        |^mail
        |mailer
        |members?
        |message
        |news(letter)?
        |noreply
        |notifications?
        |notify
        |null
        |order
        |paydirect
        |postmaster
        |reply
        |service
        |support # Should support be included as a catch all?
        |system
        |transcripts?
        |update
        |wordpress
    )
    .*?@''', re.IGNORECASE | re.VERBOSE)


BOUNCE_EMAIL_ADDRESS = re.compile(r'(^postmaster|mailer-daemon)', re.IGNORECASE)
BOUNCE_EMAIL_SUBJECT = re.compile(r'^(delivery status notification|undeliverable)', re.IGNORECASE)

FORWARDED_SUBJECT_REGEX = re.compile(r'^(fwd?|forward(ed)?):', re.IGNORECASE)

REPLY_SUBJECT_REGEX = re.compile(r'^re:', re.IGNORECASE)


SYSTEM_GENERATED_TIMES = re.compile(r'((?:[1-2][0-9]|30|31|0?[1-9])(?:[ ]?[\/][ ]?)(?:0?[1-9]|1[0-2])(?:[ ]?[\/][ ]?)(?:(?:2?0?1[0-6]|2?0?0[0-9]))|(?:[1-2][0-9]|30|31|0?[1-9])(?:[ ]?[\-][ ]?)(?:0?[1-9]|1[0-2])(?:[ ]?[\-][ ]?)(?:(?:2?0?1[0-6]|2?0?0[0-9]))|(?:[1-2][0-9]|30|31|0?[1-9])(?:[ ]?[,][ ]?)(?:0?[1-9]|1[0-2])(?:[ ]?[,][ ]?)(?:(?:2?0?1[0-6]|2?0?0[0-9]))|(?:[1-2][0-9]|30|31|0?[1-9])(?:[ ])(?:0?[1-9]|1[0-2])(?:[ ])(?:(?:2?0?1[0-6]|2?0?0[0-9]))|(?:0?[1-9]|1[0-2])(?:[ ]?[\/][ ]?)(?:[1-2][0-9]|30|31|0?[1-9])(?:[ ]?[\/][ ]?)(?:(?:2?0?1[0-6]|2?0?0[0-9]))|(?:0?[1-9]|1[0-2])(?:[ ]?[\-][ ]?)(?:[1-2][0-9]|30|31|0?[1-9])(?:[ ]?[\-][ ]?)(?:(?:2?0?1[0-6]|2?0?0[0-9]))|(?:0?[1-9]|1[0-2])(?:[ ]?[,][ ]?)(?:[1-2][0-9]|30|31|0?[1-9])(?:[ ]?[,][ ]?)(?:(?:2?0?1[0-6]|2?0?0[0-9]))|(?:0?[1-9]|1[0-2])(?:[ ])(?:[1-2][0-9]|30|31|0?[1-9])(?:[ ])(?:(?:2?0?1[0-6]|2?0?0[0-9]))|(?:(?:2?0?1[0-6]|2?0?0[0-9]))(?:[ ]?[\/][ ]?)(?:0?[1-9]|1[0-2])(?:[ ]?[\/][ ]?)(?:[1-2][0-9]|30|31|0?[1-9])|(?:(?:2?0?1[0-6]|2?0?0[0-9]))(?:[ ]?[\-][ ]?)(?:0?[1-9]|1[0-2])(?:[ ]?[\-][ ]?)(?:[1-2][0-9]|30|31|0?[1-9])|(?:(?:2?0?1[0-6]|2?0?0[0-9]))(?:[ ]?[,][ ]?)(?:0?[1-9]|1[0-2])(?:[ ]?[,][ ]?)(?:[1-2][0-9]|30|31|0?[1-9])|(?:(?:2?0?1[0-6]|2?0?0[0-9]))(?:[ ])(?:0?[1-9]|1[0-2])(?:[ ])(?:[1-2][0-9]|30|31|0?[1-9])|(?:(?:2?0?1[0-6]|2?0?0[0-9]))(?:[ ]?[\/][ ]?)(?:[1-2][0-9]|30|31|0?[1-9])(?:[ ]?[\/][ ]?)(?:0?[1-9]|1[0-2])|(?:(?:2?0?1[0-6]|2?0?0[0-9]))(?:[ ]?[\-][ ]?)(?:[1-2][0-9]|30|31|0?[1-9])(?:[ ]?[\-][ ]?)(?:0?[1-9]|1[0-2])|(?:(?:2?0?1[0-6]|2?0?0[0-9]))(?:[ ]?[,][ ]?)(?:[1-2][0-9]|30|31|0?[1-9])(?:[ ]?[,][ ]?)(?:0?[1-9]|1[0-2])|(?:(?:2?0?1[0-6]|2?0?0[0-9]))(?:[ ])(?:[1-2][0-9]|30|31|0?[1-9])(?:[ ])(?:0?[1-9]|1[0-2]))(?:[ ,aton]{0,6}?)((?:[ ]|^|[^\d\.\:\r\n$£])(?:1[0-9]|2[0-4]|0?[1-9]|00|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)[ ]?[\:\. ][ ]?(?:[0-5][0-9]|fifteen|thirty|fou?rty ?five)(?::\d\d)?(?:[ ]?(?:am|pm)|[ ]?o\'?[ ]?clock)?(?:\b|$|,\b))|((?:[1-2][0-9]|30|31|0[1-9])(?:[ ]?[\/][ ]?)(?:0[1-9]|1[0-2])(?:[ ]?[\/][ ]?)(?:(?:201[0-6]|200[0-9]))|(?:[1-2][0-9]|30|31|0[1-9])(?:[ ]?[\-][ ]?)(?:0[1-9]|1[0-2])(?:[ ]?[\-][ ]?)(?:(?:201[0-6]|200[0-9]))|(?:[1-2][0-9]|30|31|0[1-9])(?:[ ]?[,][ ]?)(?:0[1-9]|1[0-2])(?:[ ]?[,][ ]?)(?:(?:201[0-6]|200[0-9]))|(?:[1-2][0-9]|30|31|0[1-9])(?:[ ])(?:0[1-9]|1[0-2])(?:[ ])(?:(?:201[0-6]|200[0-9]))|(?:0[1-9]|1[0-2])(?:[ ]?[\/][ ]?)(?:[1-2][0-9]|30|31|0[1-9])(?:[ ]?[\/][ ]?)(?:(?:201[0-6]|200[0-9]))|(?:0[1-9]|1[0-2])(?:[ ]?[\-][ ]?)(?:[1-2][0-9]|30|31|0[1-9])(?:[ ]?[\-][ ]?)(?:(?:201[0-6]|200[0-9]))|(?:0[1-9]|1[0-2])(?:[ ]?[,][ ]?)(?:[1-2][0-9]|30|31|0[1-9])(?:[ ]?[,][ ]?)(?:(?:201[0-6]|200[0-9]))|(?:0[1-9]|1[0-2])(?:[ ])(?:[1-2][0-9]|30|31|0[1-9])(?:[ ])(?:(?:201[0-6]|200[0-9]))|(?:(?:201[0-6]|200[0-9]))(?:[ ]?[\/][ ]?)(?:0[1-9]|1[0-2])(?:[ ]?[\/][ ]?)(?:[1-2][0-9]|30|31|0[1-9])|(?:(?:201[0-6]|200[0-9]))(?:[ ]?[\-][ ]?)(?:0[1-9]|1[0-2])(?:[ ]?[\-][ ]?)(?:[1-2][0-9]|30|31|0[1-9])|(?:(?:201[0-6]|200[0-9]))(?:[ ]?[,][ ]?)(?:0[1-9]|1[0-2])(?:[ ]?[,][ ]?)(?:[1-2][0-9]|30|31|0[1-9])|(?:(?:201[0-6]|200[0-9]))(?:[ ])(?:0[1-9]|1[0-2])(?:[ ])(?:[1-2][0-9]|30|31|0[1-9])|(?:(?:201[0-6]|200[0-9]))(?:[ ]?[\/][ ]?)(?:[1-2][0-9]|30|31|0[1-9])(?:[ ]?[\/][ ]?)(?:0[1-9]|1[0-2])|(?:(?:201[0-6]|200[0-9]))(?:[ ]?[\-][ ]?)(?:[1-2][0-9]|30|31|0[1-9])(?:[ ]?[\-][ ]?)(?:0[1-9]|1[0-2])|(?:(?:201[0-6]|200[0-9]))(?:[ ]?[,][ ]?)(?:[1-2][0-9]|30|31|0[1-9])(?:[ ]?[,][ ]?)(?:0[1-9]|1[0-2])|(?:(?:201[0-6]|200[0-9]))(?:[ ])(?:[1-2][0-9]|30|31|0[1-9])(?:[ ])(?:0[1-9]|1[0-2]))|(((\b(?:201[0-6]|200[0-9])\b|\b(?:monday|mon\b|tuesday|tue\b|wednesday|weds?|thursday|thur?|friday|fri\b|saturday|sat\b|sunday|sun\b)|\b(?:january|jan\b|february|feb\b|march|mar\b|april|apr\b|may\b|june|jun\b|july|jul\b|august|aug\b|september|sept?|october|oct\b|november|nov\b|december|dec\b)[ ]?(?:[1-2][0-9]|30|31|0?[1-9])?\b|(?:[ ]|^|[^\d\.\:\r\n$£])(?:1[0-9]|2[0-4]|0?[1-9]|00|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)[ ]?[\:\. ][ ]?(?:[0-5][0-9]|fifteen|thirty|fou?rty ?five)(?::\d\d)?(?:[ ]?(?:am|pm)|[ ]?o\'?[ ]?clock)?(?:\b|$|,\b)|\b(?:[1-2][0-9]|30|31|[1-9])[^\S:]|\b(?:1[0-9]th|[2-3]0th|[2-3]?1st|2?2nd|2?3rd|2?[4-9]th)\b))[ ,\-aton\D]{0,6}?){3,10}', re.I | re.M)

# https://regex101.com/r/yW4sN0
# TODO: starts with 'automatic' seems perhaps too broad, what about spelling out the variants, i.e., 'automatic reply', 'auto response', etc.
AUTORESPONDER_SUBJECT = re.compile(r'^(automatic|out of office|ooo|on (vacation|holiday)|(away from( the)?|out of) office)', re.IGNORECASE)


# https://regex101.com/r/uX7kX0
NEGATION_REGEX_PATTERN = r'''
#### NEGATIONS ####

# Busy ∂
\b(
      # wrapper
      (?:(?:from|is|i|am|at|on|it|do|to|for|a|make|the
                    |that|day|time|month|exactly
                    |call|meeting|lunch|breakfast|brunch)[ ])*?
      (?:
         # negative words
         (?:busy|can'?t|can[ ]?n?ot|unavailable|except|(?<!not[ ])booked[ ]up)
         # negated positive words
         |(?:not|∆)[ ]   (?:be|∆)?[ ]?   (?:available|free|around|do|able)
      )
      # wrapper
      [ ]?(?:(?:from|is|i|am|at|on|it|do|to|for|a|make|the
                    |that|day|time|month|exactly
                    |call|meeting|lunch|breakfast|brunch)[ ])*?
         # wrapper gets one free word
         (?:[ ]?   (?:\S+)   [ ]?)?
            # Repeat wrapper so free word can be anywhere in continuation
            [ ]?(?:(?:from|is|i|am|at|on|it|do|to|for|a|make|the
                          |that|day|time|month|exactly
                          |call|meeting|lunch|breakfast|brunch)[ ])*?
   [ ]?(∂|then|at[ ]that[ ]time)([ ](and|/|\\)[ ]∂)?
|
# ∂ Busy
   # reverse the above after everything else
∆

# am doing|at X at|on ∂
|  ( (   (\b(?:am|are|will[ ]be)\b[ ])
         (at|on|doing|\S+ing|OOO|out[ ]of[ ]office)[ ]
         # "Have a" is a special case. Can't have "a" in the second group.
#      |  (?:have|has)[ ](?:an?)[ ]
         # "Have a" also needs a negative lookahead for various false positives
#         (?! .* (?:free|open|clean?r?|fresh|blank|vacant|bare|naked) )
         # 8 Free words, no \s\r\n or ".!?"
     )   (?:[^.• !?\r\n]+[ ]){0,8}?
         # may need to come back to the below, ?'d out for now
         (?:at|on)?
   )

   (∂|then|at[ ]that[ ]time)


# REVERSE EXCEPT: "I am busy Tomorrow Except for 3-5pm"

# "I have a 3pm"
| (I[ ]have[ ]a(n)?([ ]?other)?[ ]((appointment|meeting|previous[ ]engagement)[ ])?(at[ ])?∂([ ]already)?)
)

# ∂ is more difficult for me
| (∂[ ](and|or|/|\\|,))+[ ]?(∂[ ](are|is)[ ](more[ ])?difficult[ ]for[ ]me)


# busy ∂ (and also ∂) - NO ALTERNATION
[ ]? (?:(?:(?:and|maybe|also|aswell|as| [.,?!:;] ) [ ])* (∂))?

|
∂[ ]isn'?t[ ]good[ ]for[ ]me
'''

# NEGATION_REGEX = re.compile(NEGATION_REGEX_PATTERN, re.IGNORECASE | re.VERBOSE)


# https://regex101.com/r/pR0uI5
SAVIOUR_STRINGS_REGEX_PATTERN = r'''# SAVIOUR STRINGS: Noone says "we can do X" after valid dates.They might: "We can also do X"
# "a" can't be the first word
(?!a)
# match continous strings made up of 2 groups of words
((?:(?:we|could|how|i|a|is|it|am|be|do|can|you|would|do)[ ])+   )
(
(?:(?:it|on|at|to|do|from|have|can|able|make|about|exactly|say|call|take|possible|meet|still)[ ])+
)(∂)([ ]?(or|and|,|/|\\)[ ]?∂)?'''



# If any of these words appear before a saviour string it is a false positive
SAVIOUR_STRING_NEGATOR_REGEX_PATTERN = r'''
(
    alternatively|
    also|
    as[ ]?well|
    (in[ ])?addition(ly)?
)
'''

# https://regex101.com/r/nQ1kH1/1
SAME_TIME_IN_MULTIPLE_TIMEZONES_PATTERN = r'''
    (?P<first_match>[ ]*∂[ ]*)
    (?P<subsequent_matches>
      (
        (/|\\)
        [ ]*∂[ ]*
      )+|
      \([ ]*∂[ ]*\)
    )
'''
