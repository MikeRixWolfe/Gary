import re
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
def googleimage(inp, say=None, api_key=None):
    """gis <query> - Returns an image from Google Image results for <query>."""
    try:
        parsed = custom_get(inp, api_key, is_image=True, num=1)
    except Exception as e:
        return "Error: {}".format(e)
    if 'items' not in parsed:
        return "No results"

    say(web.try_googl(parsed['items'][0]['link']))


@hook.api_key('google')
@hook.command('gif')
def googleimage_gif(inp, say=None, api_key=None):
    """gif <query> - Returns a gif from Google Image results for <query>."""
    try:
        parsed = custom_get('filetype:gif ' + inp, api_key, is_image=True, num=1)
    except Exception as e:
        return "Error: {}".format(e)
    if 'items' not in parsed:
        return "No results"

    say(web.try_googl(parsed['items'][0]['link']))


@hook.api_key('google')
@hook.command('g')
@hook.command
def google(inp, say=None, api_key=None):
    """g[oogle] <query> - Returns first Google search result for <query>."""
    try:
        parsed = custom_get(inp, api_key)
    except Exception as e:
        return "Error: {}".format(e)
    if 'items' not in parsed:
        return "No results"

    link = web.try_googl(parsed['items'][0]['link'])
    title = text.truncate_str(parsed['items'][0]['title'], 250)
    title = u' '.join(re.sub(u'\r|\n', u' ', title).split()).strip('| ')
    say(u"{} - \x02{}\x02".format(link, title))


@hook.command
def map(inp, say=None):
    """map <place>|<origin to destination> - Gets a Map of place or route from Google Maps."""
    say(web.try_googl("https://www.google.com/maps/?q={}".format(http.quote_plus(inp))))

