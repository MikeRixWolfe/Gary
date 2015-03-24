import re
from util import hook, http


@hook.command
def gex(inp):
    """.gex <amount> <from currency> [to] <to currency> - Returns Google Exchange result; <amount> and <to currency> default to 1 and USD respectively."""
    inp = re.match(r'(\d+)? ?(\w+)?(?: \w{2} | )?(\w+)?', inp.upper()).groups()
    inp = [inp[0] or '1', inp[1] or 'USD', inp[2] or 'USD']

    try:
        data = http.get_html('https://www.google.com/finance/converter',
            query_params=dict(zip(['a', 'from', 'to'], inp)))
    except Exception as e:
        return "Google Finance error: {}".format(e)

    return ''.join(data.xpath('//div[@id="currency_converter_result"]//text()')).strip() or \
        "Error converting {} {} to {}; please check your input.".format(*inp)

