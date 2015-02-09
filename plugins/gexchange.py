import re
from util import hook, http


@hook.command
def gex(inp):
    """.gex <amount> <from currency> <to currency> - Returns Google Exchange result; <amount> and <to currency> default to 1 and USD respectively."""
    inp = re.match(r'(\d+)? ?(\w+)? ?(\w+)?', inp.upper()).groups()
    inp = [inp[0] or '1', inp[1] or 'USD', inp[2] or 'USD']

    try:
        data = http.get_json('https://rate-exchange.appspot.com/currency',
            query_params=dict(zip(['q', 'from', 'to'], inp)))
    except Exception as e:
        return "Google Exchange API error: {}".format(e)

    try:
        return "{} {from} to {to} = {v} (rate: {rate})".format(inp[0], **data)
    except:
        return "Error converting {} {} to {}; please check your input.".format(*inp)

