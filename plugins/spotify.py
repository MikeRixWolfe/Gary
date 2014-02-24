from util import hook, http

import urllib2
import json
import re


def get_data(url):
    headers = {'User-agent':
               'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.13) Gecko/20080311 Firefox/2.0.0.13'}

    request = urllib2.Request(url, None, headers)
    response = urllib2.urlopen(request).read()
    response = json.loads(response)

    return response


def region_filter(data):
    tracks = data['tracks']
    track_names = []

    for track in tracks:
        if("US" in track['album']['availability']['territories'] or "worldwide" in track['album']['availability']['territories']):
            return track

    return None


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


@hook.command
def spotify(inp, say=None):
    ".spotify <query> - Searches the Spotify database for URL's to any matching songs. Replies with the first result."

    # Put together the request from bot input and the API URL
    api_url = "http://ws.spotify.com/search/1/track.json?q="
    parameters = inp.replace(" ", "+")
    request_url = api_url + parameters

    data = get_data(request_url)

    # Loop through and find a track that's available in the US
    track = region_filter(data)

    # Return the track + data, or print 'No Results'
    if(track):
        if(len(track['artists']) > 1):
            artist = "Various Artists"
        else:
            artist = track['artists'][0]['name']

        track_name = track['name']

        # Generate HTTP Spotify URL using regex
        base_url = "http://open.spotify.com/track/"

        find_id = re.compile(r'.*track:(.+)$', re.I)
        match = find_id.match(track['href'])
        track_id = match.groups()[0]

        url = base_url + track_id

        say("%s - %s: %s // spotify:track:%s" %
            (artist, track_name, url, track_id))

    else:
        return "No Results"
