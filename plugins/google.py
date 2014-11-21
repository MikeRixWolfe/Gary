import random
from util import hook, http, text, web


def api_get(kind, query):
    """Use the RESTful Google Search API"""
    url = 'http://ajax.googleapis.com/ajax/services/search/%s?v=1.0&safe=off'
    return http.get_json(url % kind, q=query)


@hook.command('gis')
def googleimage(inp):
    """.gis <query> - Returns first Google Image result for <query>."""

    parsed = api_get('images', inp)
    if not 200 <= parsed['responseStatus'] < 300:
        raise IOError('Error searching for images: {}: {}'.format(parsed['responseStatus'], ''))
    if not parsed['responseData']['results']:
        return 'No images found.'
    return web.try_googl(random.choice(parsed['responseData']['results'][:10])['unescapedUrl'])


@hook.command('g')
@hook.command
def google(inp):
    """.[g]oogle <query> - Returns first google search result for <query>."""

    parsed = api_get('web', inp)
    if not 200 <= parsed['responseStatus'] < 300:
        raise IOError('error searching for pages: {}: {}'.format(parsed['responseStatus'], ''))
    if not parsed['responseData']['results']:
        return 'No results found.'

    result = parsed['responseData']['results'][0]

    title = http.unescape(result['titleNoFormatting'])
    title = text.truncate_str(title, 100)

    return u'{} - \x02{}\x02'.format(web.try_googl(result['unescapedUrl']), title)
