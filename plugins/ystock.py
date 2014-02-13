'''
ystock.py - rewritten by MikeFightsBears 2013
'''

import random
from datetime import date, timedelta
from util import hook, http, web, stock


@hook.command
def stock(inp, say=''):
    '''.stock <symbol> - gets stock information from Yahoo.'''
    try:
        # heh, SQLI
        query = "SELECT * FROM yahoo.finance.quote WHERE symbol=@symbol LIMIT 1"
        quote = web.query(query, {"symbol": inp}).one()
    except:
        quote = stock.getstock(inp)
        if quote:
            say(quote)
            return
        else:
           return "Yahoo Fianance API error, please try again in a few minutes"

    # if we dont get a company name back, the symbol doesn't match a company
    if quote['Change'] is None:
        return "Unknown ticker symbol %s" % inp

    change = float(quote['Change'])
    price = float(quote['LastTradePriceOnly'])

    if change < 0:
        quote['color'] = "5"
    else:
        quote['color'] = "3"

    quote['PercentChange'] = 100 * change / (price - change)

    say ("%(Name)s - $%(LastTradePriceOnly)s "                   \
          "\x03%(color)s%(Change)s (%(PercentChange).2f%%)\x03 "        \
          "H: $%(DaysHigh)s L: $%(DaysLow)s " \
          "MCAP: %(MarketCapitalization)s " \
          "Volume: %(Volume)s" % quote)


@hook.command
def stockhistory(inp, say=''):
    '''.stockhisory <symbol> - gets stock history information from Yahoo.'''
    try:
        query = "SELECT * FROM yahoo.finance.quotes WHERE symbol=@symbol LIMIT 1"
        quote = web.query(query, {"symbol": inp})
        out = quote.one()
    except:
        quote = stock.getstock(inp)
        if quote:
            return quote
        else:
           return "Yahoo Fianance API error, please try again in a few minutes"

    if out['PercentChangeFromYearLow'][0] == '-':
        out['Color'] = "5"
    else:
        out['Color'] = "3"

    volchange = float(out['Volume']) - float(out['AverageDailyVolume'])
    if volchange < 0:
        out['VolColor'] = "5"
        out['VolumeChange'] = '-%d' % int(abs(round(volchange, 2)))
    else:
        out['VolColor'] = "3"
        out['VolumeChange'] = '+%d' % int(abs(round(volchange, 2)))
    out['PercentVolChange'] = round(100 * volchange / (float(out['Volume']) - volchange))

    say("%(Name)s - $%(LastTradePriceOnly)s " \
          "\x03%(Color)s%(ChangeFromYearLow)s (%(PercentChangeFromYearLow)s)\x03 " \
          "Year H: $%(YearHigh)s Year Avg: $%(TwoHundreddayMovingAverage)s " \
          "Year L: $%(YearLow)s; Volume @ %(Volume)s " \
          #"\x03%(VolColor)s%(VolumeChange)s (%(PercentVolChange)d%%)\x03 " \
          "Avg Daily Volume: %(AverageDailyVolume)s " \
          "[%(LastTradeTime)s]" % out)
