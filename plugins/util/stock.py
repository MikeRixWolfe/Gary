import json
from util import http


def getstock(symbol):
    url = "http://finance.google.com/finance/info?client=ig&format=json&q="

    try:
        quote = json.loads(http.get(url + symbol)[3:])[0]
    except:
        return False

    if quote['c'][0] == '-':
        quote['color'] = "5"
    else:
        quote['color'] = "3"

    return "%(t)s - $%(l_cur)s \x03%(color)s%(c)s (%(cp)s)\x03 [%(lt)s]" % quote

