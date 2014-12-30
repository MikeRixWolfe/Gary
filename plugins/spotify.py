import re
from urllib import urlencode

from util import hook, http, web

gateway = 'http://open.spotify.com/{}/{}'  # http spotify gw address
spuri = 'spotify:{}:{}'

spotify_re = (r'(spotify:(track|album|artist|user):([a-zA-Z0-9]+))', re.I)
http_re = (r'(open\.spotify\.com\/(track|album|artist|user)\/'
           '([a-zA-Z0-9]+))', re.I)


def sptfy(inp, sptfy=False):
    if sptfy:
        shortenurl = "http://sptfy.com/index.php"
        data = urlencode({'longUrl': inp, 'shortUrlDomain': 1, 'submitted': 1, "shortUrlFolder": 6, "customUrl": "",
                          "shortUrlPassword": "", "shortUrlExpiryDate": "", "shortUrlUses": 0, "shortUrlType": 0})
        try:
            soup = http.get_soup(shortenurl, post_data=data, cookies=True)
        except:
            return inp
        try:
            link = soup.find('div', {'class': 'resultLink'}).text.strip()
            return link
        except:
            message = "Unable to shorten URL: %s" % \
                      soup.find('div', {'class': 'messagebox_text'}).find('p').text.split("<br/>")[0]
            return message
    else:
        return web.try_googl(inp)


@hook.command
def spotify(inp):
    """.spotify [-track|-artist|-album] <search term> - Search for specified media via Spotify; defaults to track."""
    inp = inp.split(' ')
    if len(inp) > 1 and inp[0] in ['-track', '-artist', '-album']:
        kind, query = inp.pop(0)[1:], " ".join(inp)
    else:
        kind, query = "track", " ".join(inp)

    try:
        data = http.get_json("http://ws.spotify.com/search/1/{}.json".format(kind), q=query)
    except Exception as e:
        return "Could not get {} information: {}".format(kind, e)

    try:
        type, id = data[kind+"s"][0]["href"].split(":")[1:]
    except IndexError:
        return "Could not find {}.".format(kind)
    url = sptfy(gateway.format(type, id))

    if kind == 'artist':
        return u"\x02{}\x02 - {}".format(data["artists"][0]["name"], url)
    else:
        return u"\x02{}\x02 by \x02{}\x02 - {}".format(data[kind+"s"][0]["name"], data[kind+"s"][0]["artists"][0]["name"], url)


@hook.regex(*http_re)
@hook.regex(*spotify_re)
def spotify_url(match):
    type = match.group(2)
    spotify_id = match.group(3)
    url = spuri.format(type, spotify_id)
    # no error catching here, if the API is down fail silently
    try:
        data = http.get_json("http://ws.spotify.com/lookup/1/.json", uri=url)
    except:
        pass
    if type == "track":
        name = data["track"]["name"]
        artist = data["track"]["artists"][0]["name"]
        album = data["track"]["album"]["name"]
        return u"Spotify Track: \x02{}\x02 by \x02{}\x02 from the album \x02{}\x02 - {}".format(name, artist,
                                                                                                        album, sptfy(
                gateway.format(type, spotify_id)))
    elif type == "artist":
        return u"Spotify Artist: \x02{}\x02 - {}".format(data["artist"]["name"],
                                                                 sptfy(gateway.format(type, spotify_id)))
    elif type == "album":
        return u"Spotify Album: \x02{}\x02 - \x02{}\x02 - {}".format(data["album"]["artist"],
                                                                             data["album"]["name"],
                                                                             sptfy(gateway.format(type, spotify_id)))
