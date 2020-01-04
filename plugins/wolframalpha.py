import re

from util import hook, http, text


@hook.api_key('wolframalpha')
@hook.command
def wa(inp, api_key=None):
    """wa <query> - Computes <query> using Wolfram Alpha."""

    url = 'http://api.wolframalpha.com/v2/query'

    try:
        params = { 'input': inp, 'appid': api_key, 'output': 'json' }
        result = http.get_json(url, query_params=params)
    except:
        return "WolframAlpha API error, please try again in a few minutes."

    if result['queryresult']['success'] == False:
        return "WolframAlpha query failed."

    data = sorted([pod for pod in result['queryresult']['pods'] if pod['title'] != 'Input interpretation'], key= lambda x: x['position'])

    if len(data) == 0:
        return "No results."

    return text.truncate_str(data[0]['subpods'][0]['plaintext'], 230)

