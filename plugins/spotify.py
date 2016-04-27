import re
from urllib import urlencode

from util import hook, http, web

gateway = 'http://play.spotify.com/{}/{}'  # http spotify gw address
spuri = 'spotify:{}:{}'

spotify_re = (r'(spotify:(track|album|artist|user:[^:]+:playlist|user):([a-zA-Z0-9]+))', re.I)
http_re = (r'https?://((?:open|play)\.spotify\.com\/(track|album|artist|user\/[^\/]+\/playlist|user)\/'
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
        data = http.get_json("https://api.spotify.com/v1/search/", type=kind, q=query, limit=1)
    except Exception as e:
        return "Could not get {} information: {}".format(kind, e)

    try:
        type, id = data[kind+"s"]['items'][0]["uri"].split(":")[1:]
    except IndexError as e:
        return "Could not find {}.".format(kind)
    url = sptfy(gateway.format(type, id))

    if kind == 'track':
        return u"\x02{}\x02 by \x02{}\x02 - {}".format(data[kind+"s"]['items'][0]["name"], data[kind+"s"]['items'][0]["artists"][0]["name"], url)
    else:
        return u"\x02{}\x02 - {}".format(data[kind+"s"]['items'][0]["name"], url)


@hook.regex(*http_re)
@hook.regex(*spotify_re)
def spotify_url(match, say=None):
    type = match.group(2)
    spotify_id = match.group(3)
    url = spuri.format(type.replace('/', ':'), spotify_id)

    try:
        data = http.get_json("https://api.spotify.com/v1/{}s/{}".format(type, spotify_id), format='json')

        if type == "track":
            name = data["name"]
            artist = data["artists"][0]["name"]
            album = data["album"]["name"]
            say(u"{} - \x02{}\x02 by \x02{}\x02 on \x02{}\x02".format(
                sptfy(gateway.format(type, spotify_id)), name, artist, album))
        else:  # artists and albums
            say(u"{} - \x02{}\x02".format(sptfy(gateway.format(type, spotify_id)),
                data["name"]))
    except:
        try:  # anything else that requires an access token
            say(web.try_googl(match.group(0)) + " - Spotify")
        except:
            pass

