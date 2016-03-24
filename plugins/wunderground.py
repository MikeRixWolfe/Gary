from util import hook, http

wunder_url = "http://api.wunderground.com/api/{}/forecast/geolookup/conditions/q/{}.json"
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
    337.5: "NNW",
    360: "N"
}


@hook.api_key('wunder')
@hook.command('w')
@hook.command
def weather(inp, say=None, api_key=None):
    """.w[eather] <zip code|location> - Gets the current weather conditions."""
    if api_key is None:
        return "Error: API key not set."

    try:
        weather = http.get_json(wunder_url.format(api_key, http.quote_plus(inp)))
    except:
        return "Weather Underground API error, please try again in a few minutes."

    try:
        direction = cards.get(float(weather['current_observation']['wind_degrees']),
            cards[min(cards.keys(), key=lambda k: abs(k - float(weather['current_observation']['wind_degrees'])))])

        say("\x02{location[city]}, {location[state]}\x0F: {current_observation[temp_f]}*F " \
            "with {current_observation[weather]}, wind chill {current_observation[windchill_f]}*F " \
            "({current_observation[wind_mph]}MPH {}), humidity at {current_observation[relative_humidity]}.".format(direction, **weather))
    except:
        return "Error: unable to find weather data for location."


@hook.api_key('wunder')
@hook.command('f')
@hook.command
def forecast(inp, say=None, api_key=None):
    """.f[orecast] <zip code|location> - Gets the weather forecast."""
    if api_key is None:
        return "Error: API key not set."

    try:
        weather = http.get_json(wunder_url.format(api_key, http.quote_plus(inp)))
    except:
        return "Weather Underground API error, please try again in a few minutes."
    try:
        say("\x02{location[city]}, {location[state]}\x0F: ".format(**weather) +
            '; '.join(["\x02{date[weekday]}\x0F: L {low[fahrenheit]}*F, H {high[fahrenheit]}*F, {conditions}".format(**day)
            for day in weather['forecast']['simpleforecast']['forecastday']]))
    except:
        return "Error: unable to find weather data for location."

