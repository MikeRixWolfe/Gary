from util import http, hook

api_root = 'http://api.rottentomatoes.com/api/public/v1.0/'
movie_search_url = api_root + 'movies.json'
movie_reviews_url = api_root + 'movies/%s/reviews.json'


@hook.api_key('rottentomatoes')
@hook.command
def rt(inp, api_key=None):
    '.rt <title> - gets ratings for <title> from Rotten Tomatoes'

    results = http.get_json(movie_search_url, q=inp, apikey=api_key)
    if results['total'] == 0:
        return 'no results'

    movie = results['movies'][0]
    title = movie['title']
    id = movie['id']
    critics_score = movie['ratings']['critics_score']
    audience_score = movie['ratings']['audience_score']
    url = movie['links']['alternate']

    if critics_score == -1:
        return

    reviews = http.get_json(movie_reviews_url % id, apikey=api_key, review_type='all')
    review_count = reviews['total']

    fresh = critics_score * review_count / 100
    rotten = review_count - fresh

    return u"%s - critics: \x02%s%%\x02 (%s\u2191%s\u2193)" \
            " audience: \x02%s%%\x02 - %s" % (title.strip(), str(critics_score).strip(), str(fresh).strip(), str(rotten).strip(), str(audience_score).strip(' '), url.strip(' '))
