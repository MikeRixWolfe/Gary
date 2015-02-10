from datetime import datetime
from util import hook, http

api_url = "http://ws.audioscrobbler.com/2.0/?format=json"


@hook.api_key('lastfm')
@hook.command('np')
@hook.command
def nowplaying(inp, say=None, api_key=None):
    """.np/.nowplaying <user> - Gets a LastFM user's last played track."""
    try:
        response = http.get_json(api_url, method="user.getrecenttracks",
            api_key=api_key, user=inp, limit=1)
    except:
        return "LastFM API Error, please try again in a few minutes"

    if 'error' in response:
        return response["message"]
    if not "track" in response["recenttracks"] or len(response["recenttracks"]["track"]) == 0:
        return "No recent tracks found for \x02%s\x0F." % inp

    tracks = response["recenttracks"]["track"]

    if isinstance(tracks, list):  # Partially scrobbled track
        track = tracks[0]
        status = 'current track'
        date = None
    elif isinstance(tracks, dict):  # Last scrobbled track
        track = tracks
        status = 'last track'
        date = track["date"]["#text"]
    else:
        return "Error parsing track listing."

    title = track["name"]
    album = track["album"]["#text"]
    artist = track["artist"]["#text"]

    ret = u"\x02%s\x0f's %s - \x02%s\x0f" % (inp, status, title)
    if artist:
        ret += u" by \x02%s\x0f" % artist
    if album:
        ret += u" on \x02%s\x0f" % album
    if date:
        ret += u" [%s]" % (datetime.strptime(date,"%d %b %Y, %H:%M") - \
            (datetime.utcnow() - datetime.now())).strftime("%d %b %Y, %H:%M")

    say(ret)


@hook.api_key('lastfm')
@hook.command
def toptrack(inp, say=None, api_key=None):
    """.toptrack [overall|7day|1month|3month|6month|12month] <user> - Gets a LastFM user's most played track, specify time period or default to overall."""
    period, user = inp.split(' ', 1) if len(inp.split()) > 1 else ("overall", inp)

    try:
        response = http.get_json(api_url, method="user.gettoptracks",
            api_key=api_key, user=user, period=period, limit=1)
    except:
        return "LastFM API Error, please try again in a few minutes"

    if 'error' in response:
        return response["message"]
    if not "track" in response["toptracks"] or len(response["toptracks"]["track"]) == 0:
        if period == "1month":
            return "The 1month flag is currently broken in the LastFM API; a bug report has been filed."
        else:
            return "No recent tracks for user \x02{}\x0F found.".format(user)

    say(u"\x02{}\x0F's \x02{}\x0F top track is \x02{name}\x0f by \x02{artist[name]}\x0f " \
        "with a total of \x02{playcount}\x0f plays".format(user, period, **response["toptracks"]["track"]))


@hook.api_key('lastfm')
@hook.command
def topartist(inp, nick='', say=None, api_key=None):
    """.topartist [overall|7day|1month|3month|6month|12month] <user> - Gets a LastFM user's most played artist, specify time period or default to overall."""
    period, user = inp.split(' ', 1) if len(inp.split()) > 1 else ("overall", inp)

    try:
        response = http.get_json(api_url, method="user.gettopartists",
            api_key=api_key, user=user, period=period, limit=1)
    except:
        return "LastFM API Error, please try again in a few minutes"

    if 'error' in response:
        return response["message"]
    if not "artist" in response["topartists"] or len(response["topartists"]["artist"]) == 0:
        return "No recent artists for user \x02{}\x0F found.".format(user)

    say(u"\x02{}\x0F's \x02{}\x0F top artist is \x02{name}\x0f with a total of " \
        "\x02{playcount}\x0f plays".format(user, period, **response["topartists"]["artist"]))


@hook.api_key('lastfm')
@hook.command
def topfriend(inp, say=None, api_key=None):
    """.topfriend <user> - Gets a LastFM user's top friend."""
    try:
        friends = [friend["name"] for friend in http.get_json(api_url,
            method="user.getfriends", api_key=api_key, user=inp)["friends"]["user"]]
        scores = [http.get_json(api_url, method="tasteometer.compare",
            api_key=api_key, type1="user", type2="user", value1=inp, value2=friend,
            limit=1)["comparison"]["result"]["score"] for friend in friends]
        friend, score = max(dict(zip(friends, scores)).iteritems(), key=lambda x: x[1])
    except:
        return "LastFM API Error, please try again in a few minutes"

    say(u"\x02{}\x0F's top friend is \x02{}\x0F with a score of \x02{}\x0f".format(inp, friend, score))


@hook.api_key('lastfm')
@hook.command
def similar(inp, nick='', say=None, api_key=None):
    """.similar <artist> - Gets similar artists via LastFM."""
    try:
        response = http.get_json(api_url, method="artist.getsimilar",
            api_key=api_key, artist=inp.strip(), limit=5, autocorrect=1)
    except:
        return "LastFM API Error, please try again in a few minutes"

    if 'error' in response:
        return response["message"]

    try:
        artist = response["similarartists"]["@attr"]["artist"]
    except:
        return 'Artist "{}" not found.'.format(inp)

    try:
        artists = [x["name"] for x in response["similarartists"]["artist"]]
    except:
        artists = ["None found"]

    say(u"Artists similar to \"\x02{}\x0f\": {}".format(artist, u", ".join(artists)))


@hook.api_key('lastfm')
@hook.command
def genres(inp, nick='', say=None, api_key=None):
    """.genres <artist> - Gets genres for artist via LastFM."""
    try:
        response = http.get_json(api_url, method="artist.getinfo",
            api_key=api_key, artist=inp.strip(), autocorrect=1)
    except:
        return "LastFM API Error, please try again in a few minutes"

    if 'error' in response:
        return response["message"]

    try:
        tags = [x["name"] for x in response["artist"]["tags"]["tag"]]
    except:
        tags = ["None found"]
    artist = response["artist"]["name"]

    say(u"Genres for \"\x02{}\x0f\": {}".format(artist, ", ".join(tags)))
