'''rate exchange from : https://rate-exchange.appspot.com/ '''

from util import hook, http

@hook.command
def gex(inp):
    '''.gex <from currency> <to currency> <amount> - returns Google Exchange result, <from currency> and <amount> default to USD and 1 respectively if not specified'''
    main_url = 'https://rate-exchange.appspot.com/currency?'
    query = inp.decode('utf-8').split(' ', 2)
    if len(query) == 1:
        query.insert(0,'usd')
    if len(query) == 2:
        if query[1].isdigit():
            query.insert(0,'usd')
        else:
            query.append('1')
    query_url = main_url+'from='+query[0]+'&to='+query[1]
    h = http.get_json(query_url, q=query[2])
    try:
        cur_from = h["from"]
    except:
        return "My api doesn't recognize %s" % query[1]
    try:
        cur_to = h["to"]
    except:
        return "My api doesn't recognize %s" % query[0]

    cur_to = h["to"]
    rate = h["rate"]
    amount = h["v"]
    if not cur_to:
        return "could not convert " + inp

    res = '%s %s to %s = %s (rate: %s)' % (cur_from, query[2], cur_to, amount, rate)
    return res
