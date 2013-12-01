from util import http, hook

@hook.command('btc', autohelp=False)
@hook.command(autohelp=False)
def bitcoin(inp, say=None):
    ".bitcoin - gets current exchange rate for bitcoins from mtgox"
    data = http.get_json("https://data.mtgox.com/api/2/BTCUSD/money/ticker")
    data = data['data']
    ticker = {
        'buy': data['buy']['display_short'],
        'high': data['high']['display_short'],
        'low': data['low']['display_short'],
        'vol': data['vol']['display_short'],
    }
    say("Current: \x0307%(buy)s\x0f - High: \x0307%(high)s\x0f"
        " - Low: \x0307%(low)s\x0f - Volume: %(vol)s" % ticker)


@hook.command('ltc', autohelp=False)
@hook.command(autohelp=False)
def litecoin(inp, say=None):
    """litecoin - gets current exchange rate for litecoins from BTC-E"""
    data = http.get_json("https://btc-e.com/api/2/ltc_usd/ticker")
    ticker = data['ticker']
    say("Current: \x0307${!s}\x0f - High: \x0307${!s}\x0f - Low: \x0307${!s}\x0f - Volume: {!s} LTC".format(ticker['buy'],ticker['high'],ticker['low'],ticker['vol_cur']))
