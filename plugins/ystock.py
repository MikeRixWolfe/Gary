import datetime
import requests
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


#@hook.command
def stock(inp, say=''):
    """.stock <symbol> - Gets stock information from Yahoo."""
    quote = get_stock_download(inp) or get_stock_console(inp) or get_stock_rest(inp)

    if not quote:
        return "Yahoo Fianance API error, please try again in a few minutes."
    if quote.get('Volume', None) in (None, 'N/A', '0', 0):
        return "Unknown ticker symbol '%s'" % inp

    try:
        if float(quote['Change']) < 0:
            quote['Color'] = "5"
        else:
            quote['Color'] = "3"

        say("{Name} - ${LastTradePriceOnly} " \
            "\x03{Color}{Change} ({ChangeinPercent})\x0F " \
            "H:${DaysHigh} L:${DaysLow} O:${Open} " \
            "Volume:{Volume} [{LastTradeTime} {LastTradeDate}]".format(**quote))
    except:
        say("Error parsing return data, please try again later.")


#@hook.command
def stockhistory(inp, say=''):
    """.stockhisory <symbol> - Gets stock history information from Yahoo."""
    quote = get_stock_download(inp) or get_stock_console(inp) or get_stock_rest(inp)

    if not quote:
        return "Yahoo Fianance API error, please try again in a few minutes."
    if quote.get('Volume', None) in (None, 'N/A', '0', 0):
        return "Unknown ticker symbol '%s'" % inp

    try:
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
    except:
        say("Error parsing return data, please try again later.")



def get_yahoo_finance_data(symbol, start=None, end=None, interval='1m'):
    url = 'https://query1.finance.yahoo.com/v8/finance/chart/{}'.format(symbol)
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.json()


def format_finance_data(data):
    indicators = data['chart']['result'][0]['indicators']['quote'][0]
    timestamps = data['chart']['result'][0]['timestamp']
    meta = data['chart']['result'][0]['meta']
    quotes = []

    for i, ts in enumerate(timestamps):
        quotes.append({
            'volume': indicators['volume'][i],
            'close': indicators['close'][i],
            'high': indicators['high'][i],
            'open': indicators['open'][i],
            'low': indicators['low'][i],
            'timestamp': ts,
            'time': datetime.datetime.fromtimestamp(ts).strftime('%H:%M %m/%d/%Y')
        })

    quotes = [quote for quote in quotes if meta['currentTradingPeriod']['regular']['start'] <= quote['timestamp'] <= meta['currentTradingPeriod']['regular']['end']]

    i = -1
    while quotes[i]['close'] is None:
        i -= 1

    quote = quotes[i]
    quote['high'] = max(indicators['high'])
    quote['low'] = min(val for val in indicators['low'] if val is not None)
    quote['open'] = indicators['close'][0]

    meta = {k: v for k, v in meta.items() if k in ['symbol', 'previousClose', 'currency', 'timezone', 'instrumentType']}

    return dict(quote.items() + meta.items())


@hook.command
def stock(inp, say=''):
    """.stock <symbol> - Gets stock information from Yahoo."""
    try:
        quote = format_finance_data(get_yahoo_finance_data(inp))
    except Exception as e:
        print(e)
        say("Unable to parse financial data, it is possible Yahoo removed this API endpoint. Please try again in a few minutes.")
        return

    quote['change'] = quote['close'] - quote['previousClose']
    quote['changeInPercent'] = float(quote['change']) / (abs(float(quote['change'])) + float(quote['close'])) * 100

    if float(quote['change']) < 0:
        quote['color'] = "5"
    else:
        quote['color'] = "3"

    say("{symbol} - ${close:.2f} " \
        "\x03{color}{change:+.2f} ({changeInPercent:.2f}%)\x0F " \
        "H:${high:.2f} L:${low:.2f} O:${open:.2f} " \
        "Volume:{volume} [{time}]".format(**quote))

