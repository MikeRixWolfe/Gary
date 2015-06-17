import random
from util import hook, http, text, web

base_url = 'https://www.googleapis.com/customsearch/v1'


def custom_get(query, key, is_image=None, num=1):
    params = {
        "q": query,
        "cx": key['cx'],
        "key": key['access'],
        "num": num,
        "fields": "items(title,link,snippet)",
        "safe": "off"
    }

    if is_image:
        params["searchType"] = "image"

    return http.get_json(base_url, query_params=params)


@hook.api_key('google')
@hook.command('gis')
def googleimage(inp, api_key=None):
    """.gis <query> - Returns a random image from the first 10 Google Image results for <query>."""
    try:
        parsed = custom_get(inp, api_key, is_image=True, num=10)
    except Exception as e:
        return "Error: {}".format(e)
    if 'items' not in parsed:
        return "No results"

    return web.try_googl(random.choice(parsed['items'])['link'])


@hook.api_key('google')
@hook.command('g')
@hook.command
def google(inp, api_key=None):
    """.g[oogle] <query> - Returns first Google search result for <query>."""
    try:
        parsed = custom_get(inp, api_key)
    except Exception as e:
        return "Error: {}".format(e)
    if 'items' not in parsed:
        return "No results"

    link = web.try_googl(parsed['items'][0]['link'])
    title = text.truncate_str(parsed['items'][0]['title'], 250)

    return u"{} - \x02{}\x02".format(link, title)


@hook.command
def map(inp):
    """.map <place>|<origin to destination> - Gets a Map of place or route from Google Maps."""
    return web.try_googl("https://www.google.com/maps/?q={}".format(http.quote_plus(inp)))


@hook.command
def lmgtfy(inp, say=''):
    """.lmgtfy <query> - Posts a Google link for the specified phrase."""
    say(web.try_googl("http://lmgtfy.com/?q={}".format(http.quote_plus(inp))))

