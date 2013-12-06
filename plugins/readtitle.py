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
v0.8    added url hooks from all other plugins
'''
import re, time, locale, random
from bs4 import BeautifulSoup
from util import hook, http, web, text
from random import choice

html_re = (r'https?\://(www\.)?\w+\.[a-zA-Z]{2,5}(\S)+', re.I)

skipurls = ["youtube","youtu.be","tinyurl", "rd.io", "rdio", "reddit", "spotify", "open.spotify.com", "steam"]

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
        if 'artist' in info and 'album' in info:  #Track
            name = info['name']
            artist = info['artist']
            album = info['album']
            return u"Rdio track: \x02{}\x02 by \x02{}\x02 - {}".format(name, artist, album)
        elif 'artist' in info and not 'album' in info:  #Album
            name = info['name']
            artist = info['artist']
            return u"Rdio album: \x02{}\x02 by \x02{}\x02".format(name, artist)
        else:  #Artist
            name = info['name']
            return u"Rdio artist: \x02{}\x02".format(name)


reddit_re = (r'.*((www\.)?reddit\.com/r[^ ]+)', re.I)

@hook.regex(*reddit_re)
def reddit_url(match):
    thread = http.get_html(match.group(0))

    title = thread.xpath('//title/text()')[0]
    upvotes = thread.xpath("//span[@class='upvotes']/span[@class='number']/text()")[0]
    downvotes = thread.xpath("//span[@class='downvotes']/span[@class='number']/text()")[0]
    author = thread.xpath("//div[@id='siteTable']//a[contains(@class,'author')]/text()")[0]
    timeago = thread.xpath("//div[@id='siteTable']//p[@class='tagline']/time/text()")[0]
    comments = thread.xpath("//div[@id='siteTable']//a[@class='comments']/text()")[0]

    return '\x02{}\x02 - posted by \x02{}\x02 {} ago - {} upvotes, {} downvotes - {}'.format(
        title, author, timeago, upvotes, downvotes, comments)


@hook.regex(r"(http://open\.spotify\.com/track/\S*)", re.I)
def spotify_parse(inp, say=None):
  url = inp.group(0)
  response = http.get_html(url)

  title_parse = response.xpath("//h1[@itemprop='name']")
  artist_parse = response.xpath("//h2/a")
  title = title_parse[0].text_content()
  artist = artist_parse[0].text_content()

  say("Spotify: %s - %s" % (artist, title))

@hook.regex(r"spotify:track:(\S*)", re.I)
def spotify_parse_uri(inp, say=None):
  url = "http://open.spotify.com/track/%s" % inp.group(1)
  response = http.get_html(url)

  title_parse = response.xpath("//h1[@itemprop='name']")
  artist_parse = response.xpath("//h2/a")
  title = title_parse[0].text_content()
  artist = artist_parse[0].text_content()

  say("Spotify: %s - %s" % (artist, title))

steam_re = (r'(.*:)//(store.steampowered.com)(:[0-9]+)?(.*)', re.I)

@hook.regex(*steam_re)
def steam_url(match):
    return get_steam_info("http://store.steampowered.com" + match.group(4))

def get_steam_info(url):
    # we get the soup manually because the steam pages have some odd encoding troubles
    page = http.get(url)
    soup = BeautifulSoup(page, 'lxml', from_encoding="utf-8")

    name = soup.find('div', {'class': 'apphub_AppName'}).text
    desc = ": " + text.truncate_str(soup.find('div', {'class': 'game_description_snippet'}).text.strip())

    # the page has a ton of returns and tabs
    details = soup.find('div', {'class': 'glance_details'}).text.strip().split(u"\n\n\r\n\t\t\t\t\t\t\t\t\t")
    genre = " - Genre: " + details[0].replace(u"Genre: ", u"")
    date = " - Release date: " + details[1].replace(u"Release Date: ", u"")
    price = ""
    if not "Free to Play" in genre:
        price = " - Price: " + soup.find('div', {'class': 'game_purchase_price price'}).text.strip()

    return name + desc + genre + date + price


