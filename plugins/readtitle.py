'''
Reads (or attempts to) the <title> tags from an HTML page
v0.1    regex should only match something ending in .htm or .html
v0.2    fuck it just match anything (and some basic error handling)
v0.3    check if one of the other regex plugins is gonna respond to this url
        and if so just return out.
v0.4    cant write regex to save my life so used split to break match at whitespace
        in case someone posts a URL and also says something about it afterwards
v0.5    if any(): return used to handle the keywords to not match urls against
v0.6    changed regex again!
v0.7    inserted isgd link to beginning of each title
'''
import re
import time
import locale
import random
from util import hook, http, web, text

html_re = (r'https?\://(www\.)?\w+\.[a-zA-Z]{2,5}(\S)+', re.I)

skipurls = ["youtube", "youtu.be", "tinyurl", "j.mp", "rd.io",
            "rdio", "reddit", "spotify", "open.spotify.com", "steam"]


@hook.regex(*html_re)
def readtitle(match, say=None, nick=None):
    parsed_url = match.group().split(' ')[0]
    if any(word in parsed_url for word in skipurls):
        return
    try:
        request_url = http.get_html(parsed_url)
    except http.HTTPError as e:
        errors = {400: 'bad request (ratelimited?) 400',
                  401: 'unauthorized 401 ',
                  403: 'forbidden 403',
                  404: 'invalid user/id 404',
                  500: 'something is broken 500',
                  502: 'something is down ("getting upgraded?") 502',
                  503: 'something is overloaded 503',
                  410: 'something something 410'}
        if e.code == 404:
            return 'bad url?'
        if e.code in errors:
            return 'error: ' + errors[e.code]
        return 'error: unknown %s' % e.code

    try:
        titleget = request_url.xpath('//title/text()')[0]
        titleuni = " - " + unicode(titleget.strip())
    except IndexError:
        titleuni = ""

    shorturl = web.try_isgd(parsed_url)

    say(shorturl + titleuni)


@hook.regex(r'(?i)http://(?:www\.)?[tinyurl.com|j.mp]/([A-Za-z0-9\-]+)')
def tinyurl(inp, say=''):
    try:
        say(http.open(inp.group()).url.strip())
    except http.URLError as e:
        pass
