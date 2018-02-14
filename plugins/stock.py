import requests
from util import hook


@hook.command
def stock(inp, say=''):
    """.stock <symbol> - Gets stock information from IEX."""
    # https://iextrading.com/developer/docs/#quote
    quote = requests.get('https://api.iextrading.com/1.0/stock/{}/quote'.format(inp))

    if quote.status_code == 404:
        return "Unknown ticker symbol '{}'".format(inp)
    elif quote.status_code != 200:
        return "IEX Trading API error, please try again in a few minutes."

    quote = quote.json()

    try:
        if float(quote['change']) < 0:
            quote['color'] = "5"
        else:
            quote['color'] = "3"

        say("{companyName} - ${latestPrice:.2f} " \
            "\x03{color}{change:+.2f} ({changePercent:.2%})\x0F " \
            "H:${high:.2f} L:${low:.2f} O:${open:.2f} " \
            "Volume:{latestVolume} [{latestTime}]".format(**quote))
    except:
        say("Error parsing return data, please try again later.")

