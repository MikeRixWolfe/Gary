from util import hook, http

import urllib2
import json
import re


@hook.command()
def gstock(inp, say=None):
    ".gstock <symbol> / .gstock <exchange>:<symbol> - Returns the current value of a given stock, default market is NASDAQ. Automatically searches for symbols given company names."
    url = "http://finance.google.com/finance/info?client=ig&format=json&q="

    try:
        quote = json.loads(http.get(url + inp)[3:])[0]
    except:
        return "Google Finance API error, please try again in a few minutes"

    if quote['c'][0] == '-':
        quote['color'] = "5"
    else:
        quote['color'] = "3"

    say("%(t)s - $%(l_cur)s \x03%(color)s%(c)s (%(cp)s)\x03 [%(lt)s]" % quote)
