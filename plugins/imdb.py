import re
from util import hook, http, web


omdbapi_url = "http://www.omdbapi.com/"
imdb_re = (r'(?:imdb.com/title/)([a-zA-Z0-9]+)', re.I)


@hook.api_key('omdb')
@hook.regex(*imdb_re)
def imdb_url(match, say=None, api_key=None):
    inp = match.group(1)

    try:
        content = http.get_json("http://www.omdbapi.com/", apikey=api_key, i=inp, plot='short', r='json')
    except:
        return "API timeout, please try again in a few seconds."

    if content['Response'] == 'False':
        return content['Error']
    elif content['Response'] == 'True':
        content['URL'] = 'http://www.imdb.com/title/%(imdbID)s' % content

        out = '\x02%(Title)s\x02 (%(Year)s) (%(Genre)s): %(Plot)s'
        if content['Runtime'] != 'N/A':
            out += ' \x02%(Runtime)s\x02.'
        if content['imdbRating'] != 'N/A' and content['imdbVotes'] != 'N/A':
            out += ' \x02%(imdbRating)s/10\x02 with \x02%(imdbVotes)s\x02 votes. '
        return out % content
    else:
        return 'Unknown error.'


@hook.api_key('omdb')
@hook.command
def imdb(inp, api_key=None):
    """.imdb <movie> [year] - Gets information about a movie from IMDb."""
    year = ""
    if inp.split()[-1].isdigit():
        inp, year = ' '.join(inp.split()[:-1]), inp.split()[-1]

    try:
        content = http.get_json("http://www.omdbapi.com/", apikey=api_key, t=inp, y=year, plot='short', r='json')
    except:
        return "API timeout, please try again in a few seconds."

    if content['Response'] == 'False':
        return content['Error']
    elif content['Response'] == 'True':
        content['URL'] = 'http://www.imdb.com/title/%(imdbID)s' % content

        out = '\x02%(Title)s\x02 (%(Year)s) (%(Genre)s): %(Plot)s'
        if content['Runtime'] != 'N/A':
            out += ' \x02%(Runtime)s\x02.'
        if content['imdbRating'] != 'N/A' and content['imdbVotes'] != 'N/A':
            out += ' \x02%(imdbRating)s/10\x02 with \x02%(imdbVotes)s\x02 votes. '
        out += web.try_googl('%(URL)s' % content)
        return out % content
    else:
        return 'Unknown error.'
