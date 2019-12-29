from util import http, hook


@hook.command('btc', autohelp=False)
@hook.command(autohelp=False)
def bitcoin(inp, say=None):
    """bitcoin - Gets current exchange rate for bitcoins from BTC-E."""
    data = http.get_json("https://btc-e.com/api/2/btc_usd/ticker")
    say("Buy: \x0307${buy}\x0f - Sell: \x0307${sell}\x0f - High: \x0307${high}\x0f - Low: \x0307${low}\x0f - Volume: {vol_cur} BTC".format(**data['ticker']))


@hook.command('ltc', autohelp=False)
@hook.command(autohelp=False)
def litecoin(inp, say=None):
    """litecoin - Gets current exchange rate for litecoins from BTC-E."""
    data = http.get_json("https://btc-e.com/api/2/ltc_usd/ticker")
    say("Buy: \x0307${buy}\x0f - Sell: \x0307${sell}\x0f - High: \x0307${high}\x0f - Low: \x0307${low}\x0f - Volume: {vol_cur} LTC".format(**data['ticker']))

