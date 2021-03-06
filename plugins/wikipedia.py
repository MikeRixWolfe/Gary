from util import hook, http, text, web


@hook.command
def wiki(inp, say=None):
    """wiki <phrase> - Gets first sentence of Wikipedia article on <phrase>."""
    try:
        search_api = u'http://en.wikipedia.org/w/api.php'
        params = { 'action': 'query', 'list': 'search',
                   'format': 'json', 'srsearch': http.quote_plus(inp) }
        search = http.get_json(search_api, query_params=params)
    except:
        return 'Error accessing Wikipedia API, please try again in a few minutes.'

    if len(search['query']['search']) == 0:
        return 'Your query returned no results, please check your input and try again.'

    try:
        params = { 'format': 'json' , 'action': 'query' , 'prop': 'info|extracts',
                   'exintro': True, 'explaintext': True, 'exchars' : 425,
                   'pageids': search['query']['search'][0]['pageid'],
                   'inprop': 'url', 'redirects': 1 }
        data = http.get_json(search_api, query_params=params)
    except:
        return 'Error accessing Wikipedia API, please try again in a few minutes.'

    data = data['query']['pages'][data['query']['pages'].keys()[0]]
    data['extract'] = data['extract'].strip('...').rsplit('.', 1)[0] + '.'
    say(u'{} - {}'.format(web.try_googl(data['fullurl']), data['extract']))

