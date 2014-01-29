'''
gexchange.py - written by MikeFightsBears 2013
'''

from util import hook, http


def isfloat(string):
    try:
        float(string)
        return True
    except ValueError:
        return False


@hook.command
def gex(inp):
    '''.gex <amount> <from currency> <to currency> - Returns Google Exchange result; <amount> and <to currency> default to 1 and USD respectively'''

    # Veryfiy and format input
    query = inp.decode('utf-8').upper().split(' ', 2)
    if len(query) == 1:
        query.append('USD')
    if len(query) == 2:
        if query[0].isdigit():
            query.append('USD')
        else:
            query.insert(0, '1')
    if len(query) == 3:
        if not (query[0].isdigit() or isfloat(query[0])):
            query[0] = 1

    # Get data
    query_url = 'https://rate-exchange.appspot.com/currency?from=' + \
        query[1] + '&to=' + query[2]

    # Return
    try:
        data = http.get_json(query_url, q=query[0])
    except:
        return "Google Exchange API error, please try again in a few minutes."
    try:
        return (
            '%s %s to %s = %s (rate: %s)' % (
                query[0],
                data["from"],
                data["to"],
                data["v"],
                data["rate"])
        )
    except:
        return (
            "I could not convert %s %s to %s; please check your input." % (
                query[0],
                query[1],
                query[2])
        )
