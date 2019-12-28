import requests
from util import hook, web

url = 'https://www.alphavantage.co/query'


def tryParse(value):
    try:
        return float(value.strip('%'))
    except ValueError:
        return value


@hook.api_key('alphavantage')
@hook.command()
def stock(inp, api_key=None):
    params = {'function': 'GLOBAL_QUOTE', 'apikey': api_key, 'symbol': inp}
    quote = requests.get(url, params=params).json()

    if not quote.get("Global Quote"):
        return "Unknown ticker symbol '{}'".format(inp)

    quote = {k.split(' ')[-1]:tryParse(v) for k,v in quote['Global Quote'].items()}

    quote['url'] = web.try_googl(inp)

    try:
        if float(quote['change']) < 0:
            quote['color'] = "5"
        else:
            quote['color'] = "3"

        return "{symbol} - ${price:.2f} " \
            "\x03{color}{change:+.2f} ({percent:.2f}%)\x0F " \
            "H:${high:.2f} L:${low:.2f} O:${open:.2f} " \
            "Volume:{volume} - {url}".format(**quote)
    except:
        return "Error parsing return data, please try again later."

