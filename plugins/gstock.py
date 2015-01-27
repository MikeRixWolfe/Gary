import json
from util import hook, http


@hook.command
def gstock(inp):
    """.gstock <symbol> - Gets stock information from Google."""
    url = "http://finance.google.com/finance/info?client=ig&format=json&q="

    try:
        quote = json.loads(http.get(url + inp)[3:])[0]
    except:
        return "Google Finance API error, please try again in a few minutes."

    if quote['c'][0] == '-':
        quote['color'] = "5"
    else:
        quote['color'] = "3"

    return "%(t)s - $%(l_cur)s \x03%(color)s%(c)s (%(cp)s%%)\x03 [%(lt)s]" % quote

