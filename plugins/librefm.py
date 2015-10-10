from datetime import datetime
from util import hook, http

api_url_libre = "https://libre.fm/2.0/?format=json"


@hook.command('lp')
@hook.command
def librefm(inp, say=None):
    """.lp/.librefm <user> - Gets a LibreFM user's last played track."""
    try:
        response = http.get_json(api_url_libre, method="user.getrecenttracks",
            user=inp, page=1, limit=1)
    except:
        return "LibreFM API Error, please try again in a few minutes."

    if 'error' in response:
        return response["message"]
    if not response["recenttracks"].get("track", None):
        return "No recent tracks found for \x02%s\x0F." % inp

    tracks = response["recenttracks"]["track"]
    track = tracks if type(tracks) == dict else tracks[0]  # *Should* be list

    if not track.get('date', False) or track.get('@attr', {}).get('nowplaying', False):
        status = 'current track'
        date = None
    else:
        status = 'last track'
        date = track["date"]["#text"]

    title = track["name"]
    album = track["album"]["#text"]
    artist = track["artist"]["#text"]

    ret = u"\x02%s\x0f's %s - \x02%s\x0f" % (inp, status, title)
    if artist:
        ret += u" by \x02%s\x0f" % artist
    if album:
        ret += u" on \x02%s\x0f" % album
    if date:
        ret += u" [%s]" % (datetime.strptime(date[:-4], "%d %b %Y %H:%M") -
            (datetime.utcnow() - datetime.now())).strftime("%d %b %Y, %H:%M")

    say(ret)
