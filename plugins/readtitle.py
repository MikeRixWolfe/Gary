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
	2013-09-25 - modified by MikeFightsBears to add a tinyurl to beginning of name
'''
import re

from util import hook, http,web

html_re = (r'https?\://(www\.)?\w+\.[a-zA-Z]{2,5}(\S)+', re.I)

skipurls = ["youtube","youtu.be","tinyurl"]

@hook.regex(*html_re)
def readtitle(match, say=None, nick=None):
    #if "bochmed" in nick.lower():
    #    return
    parsed_url = match.group().split(' ')[0]
    # say('matched {}'.format(parsed_url))
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
        410: 'something something 410' }
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


youtube_re = (r'(?:youtube.*?(?:v=|/v/)|youtu\.be/|yooouuutuuube.*?id=)'
              '([-_a-z0-9]+)', re.I)

base_url = 'http://gdata.youtube.com/feeds/api/'
url = base_url + 'videos/%s?v=2&alt=jsonc'
search_api_url = base_url + 'videos?v=2&alt=jsonc&max-results=1'
video_url = "http://youtube.com/watch?v=%s"

def get_video_description(vid_id):
    j = http.get_json(url % vid_id)

    if j.get('error'):
        return

    j = j['data']

    #out = '\x02%s\x02' % j['title']
    out =  j['title']

    if 'contentRating' in j:
        out += ' - \x034NSFW\x02'

    return out


@hook.regex(*youtube_re)
def youtube_url(match, bot=None, say=None):
    #if "autoreply" in bot.config and not bot.config["autoreply"]:
    #    return
    url = web.try_isgd(video_url % match) 
    say(url + " - " +get_video_description(match.group(1)))


@hook.regex(r'(?i)http://(?:www\.)?tinyurl.com/([A-Za-z0-9\-]+)')
def tinyurl(inp, say=''):
    try:
        say (http.open(inp.group()).url.strip())
    except http.URLError, e:
        pass

