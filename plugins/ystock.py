'''
ystock.py - rewritten by MikeFightsBears 2013
'''

import random
import datetime
from util import hook, http, web


@hook.command
def stock(inp):
    '''.stock <symbol> - gets stock information from Yahoo.'''
    try:
        # heh, SQLI
        #parsed = http.get_json(
        #    url, q='select * from yahoo.finance.quote where symbol in ("%s")' % inp)
        #quote = parsed['query']['results']['quote']
        query = "SELECT * FROM yahoo.finance.quote WHERE symbol=@symbol LIMIT 1"
        quote = web.query(query, {"symbol": inp}).one()
    except:
        #print parsed
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

    ret = "%(Name)s - $%(LastTradePriceOnly)s "                   \
          "\x03%(color)s%(Change)s (%(PercentChange).2f%%)\x03 "        \
          "H: $%(DaysHigh)s L: $%(DaysLow)s " \
          "MCAP: %(MarketCapitalization)s " \
          "Volume: %(Volume)s" % quote

    return ret


@hook.command
def stockhistory(inp):
    '''.stockhisoryt <symbol> - gets stock history information from Yahoo.'''
    try:
        parsed = http.get_json(url, q='select * from yahoo.finance.quote '
                               'where symbol in ("%s")' % inp)
        quote = parsed['query']['results']['quote']
    except:
        print parsed
        return "Yahoo Fianance API error, please try again in a few minutes"

    # if we dont get a company name back, the symbol doesn't match a company
    if quote['Change'] is None:
        return "Unknown ticker symbol %s" % inp

    parsed2 = http.get_json(url, q='select * from yahoo.finance.historicaldata'
                            ' where symbol = "%s" and startDate = "%s-01-01" and endDate = "%s-01-03"' % (inp, str(datetime.date.today())[:4], str(datetime.date.today())[:4]))  # heh, SQLI

    try:
        quotehistory = parsed2['query']['results']['quote'][-1]
    except TypeError:
        return "Historical data not available for %s" % inp

    yearopen = float(quotehistory['Open'])
    price = float(quote['LastTradePriceOnly'])

    change = price - yearopen

    if change < 0:
        quote['color'] = "5"
        strchange = '-' + str(change).strip("0")
    else:
        quote['color'] = "3"
        strchange = '+' + str(change).strip("0")

    quote['YearChange'] = strchange

    quote['PercentChange'] = 100 * change / (price - change)

    yearopenvol = int(quotehistory['Volume'])
    vol = int(quote['Volume'])

    volchange = vol - yearopenvol
    quote['YearVolChange'] = volchange

    if volchange < 0:
        quote['volcolor'] = "5"
    else:
        quote['volcolor'] = "3"

    quote['PercentVolChange'] = 100 * volchange / (vol - volchange)

    ret = "%(Name)s - $%(LastTradePriceOnly)s " \
          "\x03%(color)s%(YearChange)s (%(PercentChange).2f%%)\x03 " \
          "Year H: $%(YearHigh)s Year L: $%(YearLow)s; " \
          "Volume @ %(Volume)s " \
          "\x03%(volcolor)s%(YearVolChange)s (%(PercentVolChange).2d%%)\x03 " \
          "Avg Daily Volume: %(AverageDailyVolume)s" % quote

    return ret
