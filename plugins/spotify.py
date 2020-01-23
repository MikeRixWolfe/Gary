import re
from urllib import urlencode
from util import hook, http, web

gateway = 'http://play.spotify.com/{}/{}'  # http spotify gw address


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


@hook.api_key('spotify')
@hook.command
def spotify(inp, api_key=None):
    """spotify [-track|-artist|-album] <search term> - Search for specified media via Spotify; defaults to track."""
    if not isinstance(api_key, dict) or any(key not in api_key for key in
                                            ('username', 'password')):
        return "error: api keys not set"

    inp = inp.split(' ')
    if len(inp) > 1 and inp[0] in ['-track', '-artist', '-album']:
        kind, query = inp.pop(0)[1:], " ".join(inp)
    else:
        kind, query = "track", " ".join(inp)

    try:
        params = urlencode({'grant_type': 'client_credentials'})
        access_token = http.get_json('https://accounts.spotify.com/api/token',
            auth=True, auth_keys=api_key, get_method='POST', post_data=params)['access_token']
    except Exception as e:
        return "Could not get access token: {}".format(e)


    try:
        data = http.get_json("https://api.spotify.com/v1/search/", type=kind, q=query, limit=1,
                             headers={'Authorization': 'Bearer ' + access_token})
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

