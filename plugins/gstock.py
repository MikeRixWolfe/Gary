import json
from util import hook, http, web


@hook.command
def gstock(inp):
    """.gstock <symbol> - Gets stock information from Google."""
    # Note: NASDAQ:GOOG,NASDAQ:YHOO is a valid example input
    url = "http://finance.google.com/finance/info?client=ig&format=json&q="

    try:
        quote = json.loads(http.get(url + inp)[3:])[0]
    except:
        return "Google Finance API error, please try again in a few minutes."

    if quote['c'][0] == '-':
        quote['color'] = "5"
    else:
        quote['color'] = "3"

    quote['chart'] = web.try_googl('http://www.google.com/finance/chart?tlf=12&q=' + inp)

    return "%(t)s - $%(l)s \x03%(color)s%(c)s (%(cp)s%%)\x03 - %(chart)s [%(ltt)s]" % quote

