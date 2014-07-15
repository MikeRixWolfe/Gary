from util import hook, http

api_url = "http://ws.audioscrobbler.com/2.0/?format=json"


@hook.api_key('lastfm')
@hook.command('np', autohelp=False)
@hook.command(autohelp=False)
def nowplaying(inp, nick='', say=None, api_key=None):
    """.np/.nowplaying <user> - Gets a LastFM user's last played track."""
    user = inp or nick

    try:
        response = http.get_json(api_url, method="user.getrecenttracks",
            api_key=api_key, user=user, limit=1)
    except:
        "LastFM API Error, please try again in a few minutes"
    if 'error' in response:
        return "error: %s" % response["message"] if inp \
            else "Your nick is not a Last.fm account. Try '.lastfm username'."
    if not "track" in response["recenttracks"] or len(response["recenttracks"]["track"]) == 0:
        return "No recent tracks found for \x02%s\x0F." % user

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

    ret = "\x02%s\x0F's %s - \x02%s\x0f" % (user, status, title)
    if artist:
        ret += " by \x02%s\x0f" % artist
    if album:
        ret += " on \x02%s\x0f" % album
    if date:
        ret += " [%s]" % date

    say(ret)


@hook.api_key('lastfm')
@hook.command  # (autohelp=False)
def toptrack(inp, nick='', say=None, api_key=None):
    """.toptrack [overall|7day|1month|3month|6month|12month] <user> - gets a LastFM user's most played track, specify time period or default to overall."""
    inp = inp.strip("").split(" ")

    if len(inp) == 2:
        period = inp[0]
        user = inp[1]
    elif len(inp) == 1:
        period = "overall"
        user = inp[0]
    else:
        period = "overall"
        user = nick.strip()

    response = http.get_json(api_url, method="user.gettoptracks",
                             api_key=api_key, user=user, period=period, limit=1)

    if 'error' in response:
        if inp:  # specified a user name
            return "Error: %s" % response["message"]
        else:
            return "Your nick is not a Last.fm account. try '.lastfm username'."
    if not "track" in response["toptracks"] or len(response["toptracks"]["track"]) == 0:
        if period == "1month":
            return "The 1month flag is currently broken in the LastFM API; a bug report has been filed."
        else:
            return "No recent tracks for user \x02%s\x0F found." % user

    tracks = response["toptracks"]["track"]

    if isinstance(tracks, list):
        # if the user is listening to something, the tracks entry is a list
        # the first item is the current track
        track = tracks[0]
    elif isinstance(tracks, dict):
        # otherwise, they aren't listening to anything right now, and
        # the tracks entry is a dict representing the most recent track
        track = tracks
    else:
        return "Error parsing track listing."

    title = track["name"]
    artist = track["artist"]["name"]
    playcount = track["playcount"]

    ret = "\x02%s\x0F's \x02%s\x0F top track - \x02%s\x0f" % (user,
                                                              period, title)
    if artist:
        ret += " by \x02%s\x0f" % artist
    if playcount:
        ret += " a total of \x02%s\x0f times" % playcount

    say(ret)


@hook.api_key('lastfm')
@hook.command
def similar(inp, nick='', say=None, api_key=None):
    """.similar <artist> - Gets similar artists via LastFM."""

    response = http.get_json(api_url, method="artist.getsimilar",
                             api_key=api_key, artist=inp.strip(), limit=5, autocorrect=1)

    if 'error' in response:
        return "Error parsing the LastFM API, please try again later."

    if not "artist" in response["similarartists"] or \
            not isinstance(response["similarartists"]["artist"], list) or \
            len(response["similarartists"]["artist"]) == 0:
        return "I couldn't find that artist."

    artists = response["similarartists"]["artist"]

    ret = "Artists similar to \"\x02" + inp.strip() + "\x0f\": "
    for artist in artists:
        ret = ret + "\"\x02" + artist["name"] + "\x0f\", "
    say(ret.strip(', '))
