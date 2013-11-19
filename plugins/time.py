from util import hook, http, text
import time

api_url = 'http://api.wolframalpha.com/v2/query?format=plaintext'


def cap_first(line):
    """
    capitalises the first letter of words
    (keeps other letters intact)
    """
    line = " ".join(line .split())
    return ' '.join([(s[0].upper() if s[0].isalpha() else s[0]) + s[1:] for s in line.split(' ')])


@hook.command("time")
def time_command(inp, bot=None):
    """time <area> - Gets the time in <area>"""

    query = "current time in {}".format(inp)

    api_key = bot.config.get("api_keys", {}).get("wolframalpha", None)
    if not api_key:
        return "error: no wolfram alpha api key set"

    request = http.get_xml(api_url, input=query, appid=api_key)
    time = " ".join(request.xpath("//pod[@title='Result']/subpod/plaintext/text()"))
    time = time.replace("  |  ", ", ")

    if time:
        # nice place name for UNIX time
        if inp.lower() == "unix":
            place = "Unix Epoch"
        else:
            place = cap_first(" ".join(request.xpath("//pod[@" "title='Input interpretation']/subpod/plaintext/text()"))[16:])
        return "\x02{}\x02 - {}".format(place, time)
    else:
        return "Could not get the time for '{}'.".format(inp)


@hook.command(autohelp=False)
def beats(inp):
    """beats [what|guide]- Gets the current time in .beats (Swatch Internet Time). Optional switches for what and guide for description and conversion. """

    if inp.lower() == "what":
        return "Instead of hours and minutes, the mean solar day is divided " \
               "up into 1000 parts called \".beats\". Each .beat lasts 1 minute and" \
               " 26.4 seconds. Times are notated as a 3-digit number out of 1000 af" \
               "ter midnight. So, @248 would indicate a time 248 .beats after midni" \
               "ght representing 248/1000 of a day, just over 5 hours and 57 minute" \
               "s. There are no timezones."
    elif inp.lower() == "guide":
        return "1 day = 1000 .beats, 1 hour = 41.666 .beats, 1 min = 0.6944 .beats, 1 second = 0.01157 .beats"

    t = time.gmtime()
    h, m, s = t.tm_hour, t.tm_min, t.tm_sec

    utc = 3600 * h + 60 * m + s
    bmt = utc + 3600  # Biel Mean Time (BMT)

    beat = bmt / 86.4

    if beat > 1000:
        beat -= 1000

    return "Swatch Internet Time: @%06.2f" % beat
