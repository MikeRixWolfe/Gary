from util import hook, http


cards = {
    0: "N",
    22.5: "NNE",
    45: "NE",
    67.5: "ENE",
    90: "E",
    112.5: "ESE",
    135: "SE",
    157.5: "SSE",
    180: "S",
    202.5: "SSW",
    225: "SW",
    257.5: "WSW",
    270: "W",
    292.5: "WNW",
    315: "NW",
    337.5: "NWN",
    360: "N"
}


def get_woeid(inp, api_key):
    try:
        parsed = http.get_json("http://where.yahooapis.com/v1/places.q('%s')" % (http.quote_plus(inp)),
            appid=api_key['consumer'], format="json")
        return parsed['places']['place'][0]['woeid']
    except:
        return None


def get_weather(q):
    try:
        query = http.get_json("http://query.yahooapis.com/v1/public/yql",
            q=q, format="json")['query']['results']['channel']
    except:
        return None
    return query


@hook.api_key('yahoo')
@hook.command('w')
@hook.command
def weather(inp, say=None, api_key=None):
    """.w[eather] <zip code|location> - Gets the current weather conditions."""
    if not isinstance(api_key, dict) or any(key not in api_key for key in
            ('consumer', 'consumer_secret')):
        return "Error: API keys not set."

    if inp.isdigit():
        q='SELECT * FROM weather.forecast WHERE location="%s"' % inp
    else:
        woeid = get_woeid(inp, api_key)
        if woeid is None:
            return "Error: unable to lookup weather ID for location."
        q="SELECT * FROM weather.forecast WHERE woeid=%s" % woeid

    weather = get_weather(q)

    if not weather:
        return "Yahoo Weather API error, please try again in a few minutes."

    try:
        direction = cards.get(int(weather['wind']['direction']), cards[min(cards.keys(), key=lambda k: abs(k - int(weather['wind']['direction'])))])
    except:
        return "Error: unable to find weather data for location."

    say("\x02{location[city]}, {location[region]}\x0F: {item[condition][temp]}*{units[temperature]} " \
        "and {item[condition][text]}, wind chill {wind[chill]}*{units[temperature]} " \
        "({wind[chill]}{units[speed]} {}); Humidity at {atmosphere[humidity]}%, visibility at " \
        "{atmosphere[humidity]}{units[distance]}, barometric pressure at " \
        "{atmosphere[pressure]}.".format(direction, **weather))


@hook.api_key('yahoo')
@hook.command('f')
@hook.command
def forecast(inp, say=None, api_key=None):
    """.f[orecast] <zip code|location> - Gets the current weather conditions."""
    if not isinstance(api_key, dict) or any(key not in api_key for key in
            ('consumer', 'consumer_secret')):
        return "Error: API keys not set."

    if inp.isdigit():
        q='SELECT * FROM weather.forecast WHERE location="%s"' % inp
    else:
        woeid = get_woeid(inp, api_key)
        if woeid is None:
            return "Error: unable to lookup weather ID for location."
        q="SELECT * FROM weather.forecast WHERE woeid=%s" % woeid

    weather = get_weather(q)
    if not weather:
        return "Yahoo Weather API error, please try again in a few minutes."

    try:
        days = weather['item']['forecast']
    except:
        return "Error: unable to find weather data for location."

    say("\x02{location[city]}, {location[region]}\x0F: ".format(**weather) +
        '; '.join(["\x02{day}\x0F: L {low}*F, H {high}*F, {text}".format(**day) for day in days]))

