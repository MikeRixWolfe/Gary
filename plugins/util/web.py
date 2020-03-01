import http
import json
from urllib import urlencode


with open('config', 'r') as f:
    api_key = json.loads(f.read())['api_keys']['noxd']

short_url = "https://noxd.co"
paste_url = "https://hastebin.com"
#paste_url = "http://hasteb.in"


class ShortenError(Exception):
    def __init__(self, code, text):
        self.code = code
        self.text = text

    def __str__(self):
        return self.text


def googl(url):
    """ shortens a URL with the goo.gl API """
    postdata = urlencode({'api_key': api_key, 'link': url})

    request = http.get_json(short_url, post_data=postdata, get_method='POST')
    return "{}/{}".format(short_url, request['Id'])


def try_googl(url):
    try:
        out = googl(url)
    except:
        out = url
    return out


def haste(text, ext='txt'):
    """ pastes text to a hastebin server """
    data = http.get_json(paste_url + "/documents", post_data=text, get_method='POST')
    return "{}/{}.{}".format(paste_url, data['key'], ext)

