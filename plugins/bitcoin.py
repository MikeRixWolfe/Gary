from util import http, hook


@hook.command('btc', autohelp=False)
@hook.command(autohelp=False)
def bitcoin(inp, say=None):
    ".bitcoin - Gets current exchange rate for bitcoins from BTC-E"
    data = http.get_json("https://btc-e.com/api/2/btc_usd/ticker")
    ticker = data['ticker']
    say("Current: \x0307${!s}\x0f - High: \x0307${!s}\x0f - Low: \x0307${!s}\x0f - Volume: {!s} BTC".format(
            ticker['buy'], ticker['high'], ticker['low'], ticker['vol_cur']))


@hook.command('ltc', autohelp=False)
@hook.command(autohelp=False)
def litecoin(inp, say=None):
    "litecoin - Gets current exchange rate for litecoins from BTC-E"
    data = http.get_json("https://btc-e.com/api/2/ltc_usd/ticker")
    ticker = data['ticker']
    say("Current: \x0307${!s}\x0f - High: \x0307${!s}\x0f - Low: \x0307${!s}\x0f - Volume: {!s} LTC".format(
        ticker['buy'], ticker['high'], ticker['low'], ticker['vol_cur']))


@hook.command('dc', autohelp=False)
@hook.command('doge', autohelp=False)
@hook.command(autohelp=False)
def dogecoin(inp, say=None):
    ".dogecoin - Gets current exchange rate for dogecoins from DogeAPI"
    data = http.get("https://www.dogeapi.com/wow/?a=get_current_price&convert_to=usd&amount_doge=1000")
    say("Current: \x0307${!s}\x0f per 1000 DogeCoin".format(data))
