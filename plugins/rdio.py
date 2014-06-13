import urllib
import json
import re
from util import hook, text
import oauth2 as oauth

rdio_re = (r'(.*:)//(rd.io|www.rdio.com|rdio.com)(:[0-9]+)?(.*)', re.I)


@hook.regex(*rdio_re)
def rdio_url(match, bot=None):
    api_key = bot.config.get("api_keys", {}).get("rdio_key")
    api_secret = bot.config.get("api_keys", {}).get("rdio_secret")
    if not api_key:
        return None
    url = match.group(1) + "//" + match.group(2) + match.group(4)
    consumer = oauth.Consumer(api_key, api_secret)
    client = oauth.Client(consumer)
    response = client.request('http://api.rdio.com/1/', 'POST',
        urllib.urlencode({'method': 'getObjectFromUrl', 'url': url}))
    data = json.loads(response[1])
    info = data['result']
    if 'name' in info:
        if 'artist' in info and 'album' in info:  # Track
            name = info['name']
            artist = info['artist']
            album = info['album']
            return u"Rdio track: \x02{}\x02 by \x02{}\x02 - {}".format(name,
                    artist, album)
        elif 'artist' in info and not 'album' in info:  # Album
            name = info['name']
            artist = info['artist']
            return u"Rdio album: \x02{}\x02 by \x02{}\x02".format(name, artist)
        else:  # Artist
            name = info['name']
            return u"Rdio artist: \x02{}\x02".format(name)


def getdata(inp, types, api_key, api_secret):
    consumer = oauth.Consumer(api_key, api_secret)
    client = oauth.Client(consumer)
    response = client.request('http://api.rdio.com/1/', 'POST',
        urllib.urlencode({'method': 'search', 'query': inp, 'types': types, 'count': '1'}))
    data = json.loads(response[1])
    return data


def formatdata(info):
    if 'artist' in info and 'album' in info:  # Track
        name = info['name']
        artist = info['artist']
        album = info['album']
        url = info['shortUrl']
        return u"\x02{}\x02 by \x02{}\x02 on \x02{}\x02 - {}".format(name,
            artist, album, url)
    elif 'artist' in info and not 'album' in info:  # Album
        name = info['name']
        artist = info['artist']
        url = info['shortUrl']
        return u"\x02{}\x02 by \x02{}\x02 - {}".format(name, artist, url)
    else:  # Artist
        name = info['name']
        url = info['shortUrl']
        return u"\x02{}\x02 - {}".format(name, url)


@hook.api_key('rdio')
@hook.command
def rdio(inp, api_key=None, bot=None):
    """.rdio [-track|-artist|-album] <search term> - Search for specified or any media Rdio."""
    if not isinstance(api_key, dict) or any(key not in api_key for key in
            ('consumer', 'consumer_secret')):
        return "error: No api key set"
    else:
        api_secret, api_key = api_key.values()

    inp = inp.split(' ')
    if len(inp) > 1 and inp[0] in ['-track', '-artist', '-album']:
            kind = text.capitalize_first(inp.pop(0)[1:])
            query = " ".join(inp)
    else:
        kind, query = "Track,Album,Artist", " ".join(inp)

    data = getdata(query, kind, api_key, api_secret)
    try:
        info = data['result']['results'][0]
    except IndexError:
        return "No results."

    return formatdata(info) or "Error reading data."
