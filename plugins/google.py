import random
from util import hook, http, text, web


def custom_get(query, key, is_image=None, num=1):
    url = ('https://www.googleapis.com/customsearch/v1?cx=004144994778178413853:cmzcjpe52xq'
           '&fields=items(title,link,snippet)&safe=off' + ('&searchType=image' if is_image else ''))
    return http.get_json(url, key=key, q=query, num=num)


@hook.api_key('google')
@hook.command('gis')
def googleimage(inp, api_key=None):
    """.gis <query> - Returns first Google Image result for <query>."""
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
    """.[g]oogle <query> - Returns first google search result for <query>."""
    try:
        parsed = custom_get(inp, api_key)
    except Exception as e:
        return "Error: {}".format(e)
    if 'items' not in parsed:
        return "No results"

    link = web.try_googl(parsed['items'][0]['link'])
    title = text.truncate_str(parsed['items'][0]['title'], 250)

    return u'{} - \x02{}\x02'.format(link, title)
