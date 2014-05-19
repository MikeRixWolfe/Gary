""" web.py - handy functions for web services """

import http
import urlnorm
import json
import urllib
import urllib2
import yql

short_url = "https://www.googleapis.com/urlshortener/v1/url"
paste_url = "http://hastebin.com"
yql_env = "http://datatables.org/alltables.env"

YQL = yql.Public()


class ShortenError(Exception):
    def __init__(self, code, text):
        self.code = code
        self.text = text

    def __str__(self):
        return self.text


def googl(url):
    """ shortens a URL with the goo.gl API """
    postdata = {'longUrl':url}
    headers = {'Content-Type':'application/json'}
    req = urllib2.Request(
        short_url,
        json.dumps(postdata),
        headers
    )
    ret = urllib2.urlopen(req).read()
    request = json.loads(ret)['id']

    if not request.strip():
        raise ShortenError("Error", "None returned")
    else:
        return request


def try_googl(url):
    try:
        out = googl(url)
    except:
        out = url
    return out


def haste(text, ext='txt'):
    """ pastes text to a hastebin server """
    page = http.get(paste_url + "/documents", post_data=text)
    data = json.loads(page)
    return ("%s/%s.%s" % (paste_url, data['key'], ext))


def query(query, params={}):
    """ runs a YQL query and returns the results """
    return YQL.execute(query, params, env=yql_env)
