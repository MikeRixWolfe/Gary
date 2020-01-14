from random import choice
from util import hook, http


@hook.api_key('giphy')
@hook.command
def gif(inp, say=None, api_key=None):
    """gif/giphy <query> - Returns first giphy search result."""
    url = 'http://api.giphy.com/v1/gifs/search'
    try:
        response = http.get_json(url, q=inp, limit=5, api_key=api_key)
    except http.HTTPError as e:
        return e.msg

    try:
        say(choice(response['data'])['bitly_gif_url'])
    except:
        say('No results found.')
