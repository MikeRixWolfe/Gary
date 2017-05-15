from util import hook, http, web


def get_stock_download(inp):
    try:
        url = 'http://query.yahooapis.com/v1/public/yql?format=json'
        q = "select * from csv where url='http://download.finance.yahoo.com/d/quotes.csv?s=%s&f=nl1d1t1c1p2ohgvj5j6jkm4a2d1&e=.csv' " \
            "and columns='Name,LastTradePriceOnly,Date,LastTradeTime,Change,ChangeinPercent,Open,DaysHigh,DaysLow,Volume,ChangeFromYearLow,PercentChangeFromYearLow,YearLow,YearHigh,TwoHundreddayMovingAverage,AverageDailyVolume,LastTradeDate'" % inp
        query = http.get_json(url, q=q).get('query', '')
        quote = query.get('results', '').get('row', '')
    except:
        return None

    return quote


def get_stock_rest(inp, q='SELECT * FROM yahoo.finance.quotes WHERE symbol in ("%s")'):
    try:
        url = 'http://query.yahooapis.com/v1/public/yql?' \
            'format=json&env=store%3A%2F%2Fdatatables.org%2Falltableswithkeys'
        q = q % inp
        query = http.get_json(url, q=q, timeout=15).get('query', '')
        quote = query.get('results', '').get('quote', '')
    except:
        return None

    return quote


def get_stock_console(inp, q="SELECT * FROM yahoo.finance.quotes WHERE symbol=@symbol"):
    try:
        query = web.query(q, {"symbol": inp})
        quote = query.one()
    except:
        return None

    return quote


@hook.command
def stock(inp, say=''):
    """.stock <symbol> - Gets stock information from Yahoo."""
    quote = get_stock_download(inp) #or get_stock_console(inp) or get_stock_rest(inp)

    if not quote:
        return "Yahoo Fianance API error, please try again in a few minutes."
    if quote.get('Volume', None) in (None, 'N/A', '0', 0):
        return "Unknown ticker symbol '%s'" % inp

    if float(quote['Change']) < 0:
        quote['Color'] = "5"
    else:
        quote['Color'] = "3"

    say("{Name} - ${LastTradePriceOnly} " \
          "\x03{Color}{Change} ({ChangeinPercent})\x0F " \
          "H:${DaysHigh} L:${DaysLow} O:${Open} " \
          "Volume:{Volume} [{LastTradeTime} {LastTradeDate}]".format(**quote))


@hook.command
def stockhistory(inp, say=''):
    """.stockhisory <symbol> - Gets stock history information from Yahoo."""
    quote = get_stock_download(inp) #or get_stock_console(inp) or get_stock_rest(inp)

    if not quote:
        return "Yahoo Fianance API error, please try again in a few minutes."
    if quote.get('Volume', None) in (None, 'N/A', '0', 0):
        return "Unknown ticker symbol '%s'" % inp

    if float(quote['ChangeFromYearLow']) < 0:
        quote['Color'] = "5"
    else:
        quote['Color'] = "3"
        quote['ChangeFromYearLow'] = "+" + quote['ChangeFromYearLow']

    say("{Name} - ${LastTradePriceOnly} " \
          "\x03{Color}{ChangeFromYearLow} ({PercentChangeFromYearLow})\x0F " \
          "YearH:${YearHigh} YearAvg:${TwoHundreddayMovingAverage} " \
          "YearL:${YearLow}; Volume:{Volume} " \
          "(Avg Daily Volume:{AverageDailyVolume}) " \
          "[{LastTradeTime} {LastTradeDate}]".format(**quote))

