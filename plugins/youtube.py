import locale
import re
import time

from util import hook, http, web
from random import choice

locale.setlocale(locale.LC_ALL, '')

base_url = 'http://gdata.youtube.com/feeds/api/'
url = base_url + 'videos/%s?v=2&alt=jsonc'
search_api_url = base_url + 'videos?v=2&alt=jsonc&max-results=1'
video_url = "http://youtu.be/%s"

youtube_re = (r'(?:youtube.*?(?:v=|/v/)|youtu\.be/|yooouuutuuube.*?id=)'
              '([-_a-z0-9]+)', re.I)


@hook.regex(*youtube_re)
def youtube_url(match, bot=None, say=None):
    # if "autoreply" in bot.config and not bot.config["autoreply"]:
    #    return
    url = web.try_googl(video_url % match)
    say(url + " - " + get_video_description(match.group(1)))


def get_video_description(vid_id):
    j = http.get_json(url % vid_id)

    if j.get('error'):
        return

    j = j['data']

    out = '\x02%s\x02' % j['title']

    if 'contentRating' in j:
        out += ' - \x034NSFW\x02'

    return out


@hook.command('y')
@hook.command
def youtube(inp, say=None):
    """.youtube <query> - Returns the first YouTube search result for <query>."""

    j = http.get_json(search_api_url, q=inp)

    if 'error' in j:
        return 'error performing search'

    if j['data']['totalItems'] == 0:
        return 'no results found'

    vid_id = j['data']['items'][0]['id']

    say(get_video_description(vid_id) + " - " + video_url % vid_id)
