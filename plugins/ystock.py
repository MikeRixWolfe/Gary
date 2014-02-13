'''
ystock.py - rewritten by MikeFightsBears 2013
'''

import random
from datetime import date, timedelta
from util import hook, http, web


@hook.command
def stock(inp, say=''):
    '''.stock <symbol> - gets stock information from Yahoo.'''
    try:
        # heh, SQLI
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

    say ("%(Name)s - $%(LastTradePriceOnly)s "                   \
          "\x03%(color)s%(Change)s (%(PercentChange).2f%%)\x03 "        \
          "H: $%(DaysHigh)s L: $%(DaysLow)s " \
          "MCAP: %(MarketCapitalization)s " \
          "Volume: %(Volume)s" % quote)


@hook.command
def stockhistory(inp, say=''):
    '''.stockhisory <symbol> - gets stock history information from Yahoo.'''
    try:
        query = "SELECT * FROM yahoo.finance.historicaldata WHERE symbol=@symbol and startDate=@start and endDate=@end"
        quote = web.query(query,
            {"symbol": inp,
            "start": str(date.today()-timedelta(days=365)),
            "end": str(date.today())})
        start = quote.rows[-1]
        end = quote.rows[0]
        query2 = "SELECT * FROM yahoo.finance.quote WHERE symbol=@symbol LIMIT 1"
        current = web.query(query2, {"symbol": inp}).one()
    except:
        return "Yahoo Fianance API error, please try again in a few minutes"

    if not quote.raw['count']:
        return 'Historical data unavailable for "%s"' % inp

    #quotehistory = dict(zip(start.keys(),["%.2f" % (float(x)-float(y)) if isFloat(x) else x for x,y in zip(quote.rows[0].values(), quote.rows[-1])]))
    out = {}
    out['Name'] = current['Name']
    out['YearClose'] = end['Close']
    out['YearHigh'] = max([float(i['Close']) for i in quote.rows])
    out['YearLow'] = min([float(i['Close']) for i in quote.rows])
    out['YearAverage'] = sum([float(i['Close']) for i in quote.rows]) / quote.count

    change = float(end['Close']) - float(start['Open'])
    print change

    if change < 0:
        out['Color'] = "5"
        out['YearChange'] = '-%.2f' % abs(round(change, 2))
    else:
        out['Color'] = "3"
        out['YearChange'] = '+%.2f' % abs(round(change, 2))

    out['PercentChange'] = 100 *  change / (float(end['Close']) - change)
    out['YearVolume'] = end['Volume']
    volchange = float(end['Volume']) - float(start['Volume'])

    if volchange < 0:
        out['VolColor'] = "5"
        out['VolumeChange'] = '-%d' % int(abs(round(volchange, 2)))
    else:
        out['VolColor'] = "3"
        out['VolumeChange'] = '+%d' % int(abs(round(volchange, 2)))

    out['PercentVolChange'] = round(100 * volchange / (float(start['Volume']) - volchange))
    out['AverageVolume'] = int(round(sum([float(i['Volume']) for i in quote.rows]) / quote.count))

    say("%(Name)s - $%(YearClose)s " \
          "\x03%(Color)s%(YearChange)s (%(PercentChange).2f%%)\x03 " \
          "Year H: $%(YearHigh)s Year Avg: $%(YearAverage).2f " \
          "Year L: $%(YearLow)s; Volume @ %(YearVolume)s " \
          "\x03%(VolColor)s%(VolumeChange)s (%(PercentVolChange)d%%)\x03 " \
          "Avg Volume: %(AverageVolume)d" % out)
