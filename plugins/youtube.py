import re
from util import hook, http, web

base_url = 'https://www.googleapis.com/youtube/v3/'
search_url = base_url + 'search'
video_url = base_url + 'videos'
short_url = "http://youtu.be/"

youtube_re = (r'(?:youtube.*?(?:v=|/v/|/channel/|list=)|youtu\.be/)([-_a-z0-9]+)(\?t\=\d+)?', re.I)
output_format = u'{url} - \x02{title}\x02 - \x02{channelTitle}\x02 [{time}] [{views:,} views]'


def get_youtube_info(video_id, api_key, timestamp=None):
    params = {
        "id": video_id,
        "key": api_key['access'],
        "part": "snippet,contentDetails,statistics"
    }
    result = http.get_json(video_url, query_params=params)
    if result.get('error') or not result.get('items') or len(result['items']) < 1:
        return web.googl(short_url+video_id+(timestamp if timestamp else '')) + " - \x02Youtube\x0f"

    playtime = result['items'][0]['contentDetails']['duration'].strip('PT').lower()
    views = int(result['items'][0]['statistics'].get('viewCount', 0))
    return output_format.format(url=web.try_googl(short_url+video_id+(timestamp if timestamp else '')),
                                time=playtime, views=views, **result['items'][0]['snippet'])


@hook.api_key('google')
@hook.regex(*youtube_re)
def youtube_url(match, say=None, api_key=None):
    say(get_youtube_info(match.group(1), api_key, match.group(2)))


@hook.api_key('google')
@hook.command('y')
@hook.command('yt')
@hook.command
def youtube(inp, say=None, api_key=None):
    """youtube <query> - Returns the first YouTube search result for <query>."""
    params = {
        "q": inp,
        "key": api_key['access'],
        "part": "snippet",
        "safeSearch": "none",
        "maxResults": 1,
        "type": "video"
    }
    try:
        result = http.get_json(search_url, query_params=params)
    except Exception as e:
        return "Error accessing Youtube, please try again in a few minutes."

    if result.get('error') or not result.get('items') or len(result['items']) < 1:
        return "None found."

    say(get_youtube_info(result['items'][0]['id']['videoId'], api_key))

