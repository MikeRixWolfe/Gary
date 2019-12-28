from datetime import datetime
from time import strftime
from util import hook, http


geo_url = 'https://maps.googleapis.com/maps/api/geocode/json'
weather_url = 'https://api.darksky.net/forecast/{}/{},{}'
cards = { 0: "N", 22.5: "NNE", 45: "NE", 67.5: "ENE", 90: "E", 112.5: "ESE",
          135: "SE", 157.5: "SSE", 180: "S", 202.5: "SSW", 225: "SW", 257.5: "WSW",
          270: "W", 292.5: "WNW", 315: "NW", 337.5: "NNW", 360: "N" }


def geocode(inp, api_key):
    params = {'key': api_key, 'address': inp }
    data = http.get_json(geo_url, query_params=params)
    return data['results'][0]


@hook.api_key('darksky,google')
@hook.command('w')
@hook.command
def weather(inp, say=None, api_key=None):
    """.w[eather] <zip code|location> - Gets the current weather conditions."""
    if api_key is None:
        return "Error: API key not set."

    try:
        geo = geocode(inp, api_key['google']['access'])
    except:
        return "Google Geocoding API error, please try again in a few minutes."

    try:
        weather = http.get_json(weather_url.format(api_key['darksky'], geo['geometry']['location']['lat'], geo['geometry']['location']['lng']))
    except:
        return "DarkSky API error, please try again in a few minutes."

    try:
        direction = cards.get(float(weather['currently']['windBearing']),
            cards[min(cards.keys(), key=lambda k: abs(k - float(weather['currently']['windBearing'])))])

        say(u"\x02{location}\x0F: {currently[temperature]:.0f}\u00b0F " \
            u"and {currently[summary]}, feels like {currently[apparentTemperature]:.0f}\u00b0F, " \
            u"wind at {currently[windSpeed]:.0f} ({currently[windGust]:.0f} gust) MPH {direction}, " \
            u"humidity at {currently[humidity]:.0%}.".format(direction=direction,
            location=geo['formatted_address'], **weather))
    except:
        return "Error: unable to find weather data for location."


@hook.api_key('darksky,google')
@hook.command('f')
@hook.command
def forecast(inp, say=None, api_key=None):
    """.f[orecast] <zip code|location> - Gets the weather forecast."""
    if api_key is None:
        return "Error: API key not set."

    try:
        geo = geocode(inp, api_key['google']['access'])
    except:
        return "Google Geocoding API error, please try again in a few minutes."

    try:
        weather = http.get_json(weather_url.format(api_key['darksky'], geo['geometry']['location']['lat'], geo['geometry']['location']['lng']))
    except:
        return "DarkSky API error, please try again in a few minutes."

    try:
        for day in weather['daily']['data']:
            day['day'] = datetime.fromtimestamp(day['time']).strftime("%A")
        say(u"\x02{location}\x0F: ".format(location=geo['formatted_address']) +
            u"; ".join([u"\x02{day}\x0F: L {temperatureLow:.0f}\u00b0F, H {temperatureHigh:.0f}\u00b0F, {summary}".format(**day)
            for day in weather['daily']['data'][0:5]]))
    except:
        return "Error: unable to find weather data for location."


@hook.api_key('darksky,google')
@hook.command('h')
@hook.command
def hourly(inp, say=None, api_key=None):
    """.h[ourly] <zip code|location> - Gets the 12 hour weather forecast."""
    if api_key is None:
        return "Error: API key not set."

    try:
        geo = geocode(inp, api_key['google']['access'])
    except:
        return "Google Geocoding API error, please try again in a few minutes."

    try:
        weather = http.get_json(weather_url.format(api_key['darksky'], geo['geometry']['location']['lat'], geo['geometry']['location']['lng']))
    except:
        return "DarkSky API error, please try again in a few minutes."

    try:
        for hour in weather['hourly']['data']:
            hour['hour'] = datetime.fromtimestamp(hour['time']).strftime("%-I%p")
        say(u"\x02{location}\x0F: ".format(location=geo['formatted_address']) +
            u"; ".join([u"\x02{hour}\x0F: {temperature:.0f}\u00b0F ({apparentTemperature:.0f}\u00b0F feel), {summary}".format(**hour)
            for hour in weather['hourly']['data'][0:10]]))
    except:
        return "Error: unable to find weather data for location."

