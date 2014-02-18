'''
ystock.py - rewritten by MikeFightsBears 2013
'''

import random
from datetime import date, timedelta
from util import hook, http, web


def get_stock_download(inp):
    try:
        url = 'http://query.yahooapis.com/v1/public/yql?format=json'
        q = "select * from csv where url='http://download.finance.yahoo.com/d/quotes.csv?s=%s&f=sl1d1t1c1ohgv&e=.csv' " \
            "and columns='Name,LastTradePriceOnly,Date,LastTradeTime,Change,Open,DaysHigh,DaysLow,Volume'" % inp
        query = http.get_json(url, q = q).get('query', '')
        quote = query.get('results', '').get('row', '')
        quote['PercentChange'] = "%.2f" % (float(quote['Change']) / float(quote['Open']) * 100)
    except:
        return None

    return quote


def get_stock_rest(inp, q='SELECT * FROM yahoo.finance.quotes WHERE symbol in ("%s")'):
    try:
        url = 'http://query.yahooapis.com/v1/public/yql?' \
            'format=json&env=store%3A%2F%2Fdatatables.org%2Falltableswithkeys'
        q = q % inp
        query = http.get_json(url, q = q, timeout = 15).get('query', '')
        quote = query.get('results', '').get('quote', '')
    except:
        return None

    return quote


def get_stock_console(inp, q="SELECT * FROM yahoo.finance.quotes WHERE symbol=@symbol LIMIT 1"):
    try:
        query = web.query(q, {"symbol": inp})
        quote = query.one()
    except:
        return None

    return quote


@hook.command
def stock(inp, say=''):
    '''.stock <symbol> - Gets stock information from Yahoo.'''
    quote = get_stock_rest(inp) or get_stock_download(inp)

    if not quote:
        return "Yahoo Fianance API error, please try again in a few minutes."
    if quote.get('Volume', None) in (None, 'N/A'):
        return "Unknown ticker symbol '%s'" % inp

    if float(quote['Change']) < 0:
        quote['Color'] = "5"
    else:
        quote['Color'] = "3"

    say("%(Name)s - $%(LastTradePriceOnly)s " \
          "\x03%(Color)s%(Change)s (%(PercentChange)s)\x03 " \
          "H:$%(DaysHigh)s L:$%(DaysLow)s O:$%(Open)s " \
          "Volume:%(Volume)s [%(LastTradeTime)s]" % quote)


@hook.command
def stockhistory(inp, say=''):
    '''.stockhisory <symbol> - gets stock history information from Yahoo.'''
    quote = get_stock_console(inp) or get_stock_rest(inp,
        'SELECT * FROM yahoo.finance.quotes WHERE symbol in ("%s")')

    if not quote:
        return "Yahoo Fianance API error, please try again in a few minutes."
    if quote.get('Volume', None) in (None, 'N/A'):
        return "Unknown ticker symbol '%s'" % inp

    if float(quote['Change']) < 0:
        quote['Color'] = "5"
    else:
        quote['Color'] = "3"

    say("%(Name)s - $%(LastTradePriceOnly)s " \
          "\x03%(Color)s%(ChangeFromYearLow)s (%(PercentChangeFromYearLow)s)\x03 " \
          "Year H: $%(YearHigh)s Year Avg: $%(TwoHundreddayMovingAverage)s " \
          "Year L: $%(YearLow)s; Volume @ %(Volume)s " \
          "(Avg Daily Volume: %(AverageDailyVolume)s) " \
          "[%(LastTradeTime)s]" % quote)
