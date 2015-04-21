import re
from util import hook, http, web

base_url = 'https://www.googleapis.com/youtube/v3/'
search_url = base_url + 'search'
video_url = base_url + 'videos'
short_url = "http://youtu.be/"

youtube_re = (r'(?:youtube.*?(?:v=|/v/)|youtu\.be/|yooouuutuuube.*?id=)'
              '([-_a-z0-9]+)', re.I)


@hook.api_key('google')
@hook.regex(*youtube_re)
def youtube_url(match, say=None, api_key=None):
    params = {
        "id": match.group(1),
        "key": api_key['access'],
        "part": "snippet"
    }
    result = http.get_json(video_url, query_params=params)

    if result.get('error') or not result.get('items') or len(result['items']) < 1:
        return

    say('{} - \x02{title}\x02'.format(web.try_googl(short_url+ match.group(1)),
        **result['items'][0]['snippet']))


@hook.api_key('google')
@hook.command('y')
@hook.command('yt')
@hook.command
def youtube(inp, say=None, api_key=None):
    """.youtube <query> - Returns the first YouTube search result for <query>."""
    params = {
        "q": inp,
        "key": api_key['access'],
        "part": "snippet",
        "safeSearch": "none",
        "maxResults": 1,
        "order": "viewCount",
        "type": "video"
    }
    result = http.get_json(search_url, query_params=params)

    if result.get('error') or not result.get('items') or len(result['items']) < 1:
        return "None found."

    video = result['items'][0]
    say("{} - \x02{title}\x02".format(web.try_googl(short_url+video['id']['videoId']),
        **video['snippet']))

