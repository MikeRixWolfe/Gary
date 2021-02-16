from datetime import datetime, timedelta
from util import hook, http


cards = { 0: "N", 22.5: "NNE", 45: "NE", 67.5: "ENE", 90: "E", 112.5: "ESE",
          135: "SE", 157.5: "SSE", 180: "S", 202.5: "SSW", 225: "SW", 257.5: "WSW",
          270: "W", 292.5: "WNW", 315: "NW", 337.5: "NNW", 360: "N" }


def strftime(time):
    return datetime.fromtimestamp(time).strftime("%p %A").replace('AM', 'early').replace('PM', 'late')


@hook.api_key('google,openweather')
@hook.command('w')
@hook.command
def weather(inp, say=None, api_key=None):
    """w[eather] <zip code|location> - Gets the current weather conditions."""
    if api_key is None:
        return "Error: API key not set."

    try:
        geo_url = 'https://maps.googleapis.com/maps/api/geocode/json'
        params = {'key': api_key['google']['access'], 'address': inp}
        geo = http.get_json(geo_url, query_params=params)['results'][0]
    except:
        return "Google Geocoding API error, please try again in a few minutes."

    try:
        owm_url = 'https://api.openweathermap.org/data/2.5/onecall'
        params = {'lat': geo['geometry']['location']['lat'], 'lon': geo['geometry']['location']['lng'],
            'appid': api_key['openweather'], 'exclude': 'minutely', 'units': 'imperial'}
        weather = http.get_json(owm_url, query_params=params)
    except:
        return "OpenWeather API error, please try again in a few minutes."

    try:
        direction = cards.get(float(weather['current']['wind_deg']),
            cards[min(cards.keys(), key=lambda k: abs(k - float(weather['current']['wind_deg'])))])

        weather['current']['wind_gust'] = weather['current'].get('wind_gust', weather['current']['wind_speed'])

        alerts = [a for a in weather.get('alerts', []) if 'Watch' in a['event'] or ('Warning' in a['event'] and
            a['event'].replace('Warning', 'Watch') not in [x['event'] for x in weather.get('alerts', [])])]
        alerts = sorted([min(filter(lambda x: x['event'] == t, alerts), key=lambda x: x['start']) for t in
            set(a['event'] for a in alerts)], key=lambda x: x['start'])
        alerts = ', '.join(['\x02{}\x0F until \x02{}\x0F'.format(a['event'], strftime(a['end'])) for a in alerts])

        say(u"\x02{location}\x0F: {current[temp]:.0f}\u00b0F " \
            u"with {current[weather][0][description]}, feels like {current[feels_like]:.0f}\u00b0F, " \
            u"wind at {current[wind_speed]:.0f} MPH ({current[wind_gust]:.0f} MPH gust) {direction}, " \
            u"humidity at {current[humidity]:.0f}%. {alert}".format(direction=direction,
            location=geo['formatted_address'], alert=alerts, **weather))
    except:
        return "Error: unable to find weather data for location."


@hook.api_key('google,openweather')
@hook.command('h')
@hook.command
def hourly(inp, say=None, api_key=None):
    """h[ourly] <zip code|location> - Gets the 10 hour weather forecast."""
    if api_key is None:
        return "Error: API key not set."

    try:
        geo_url = 'https://maps.googleapis.com/maps/api/geocode/json'
        params = {'key': api_key['google']['access'], 'address': inp}
        geo = http.get_json(geo_url, query_params=params)['results'][0]
    except:
        return "Google Geocoding API error, please try again in a few minutes."

    try:
        owm_url = 'https://api.openweathermap.org/data/2.5/onecall'
        params = {'lat': geo['geometry']['location']['lat'], 'lon': geo['geometry']['location']['lng'],
            'appid': api_key['openweather'], 'exclude': 'minutely', 'units': 'imperial'}
        weather = http.get_json(owm_url, query_params=params)
    except:
        return "OpenWeather API error, please try again in a few minutes."

    try:
        for hour in weather['hourly']:
            hour['hour'] = (datetime.utcfromtimestamp(hour['dt']) + timedelta(seconds=weather['timezone_offset'])).strftime("%-I%p")
        say(u"\x02{location}\x0F: ".format(location=geo['formatted_address']) +
            u". ".join([u"\x02{hour}\x0F: {temp:.0f}\u00b0F ({feels_like:.0f}\u00b0F feel), {weather[0][description]}".format(**hour)
            for hour in weather['hourly'][0:10]]))
    except:
        return "Error: unable to find weather data for location."


@hook.api_key('google,openweather')
@hook.command('fc')
@hook.command
def forecast(inp, say=None, api_key=None):
    """forecast/fc <zip code|location> - Gets the 7 day weather forecast."""
    if api_key is None:
        return "Error: API key not set."

    try:
        geo_url = 'https://maps.googleapis.com/maps/api/geocode/json'
        params = {'key': api_key['google']['access'], 'address': inp}
        geo = http.get_json(geo_url, query_params=params)['results'][0]
    except:
        return "Google Geocoding API error, please try again in a few minutes."

    try:
        owm_url = 'https://api.openweathermap.org/data/2.5/onecall'
        params = {'lat': geo['geometry']['location']['lat'], 'lon': geo['geometry']['location']['lng'],
            'appid': api_key['openweather'], 'exclude': 'minutely', 'units': 'imperial'}
        weather = http.get_json(owm_url, query_params=params)
    except:
        return "OpenWeather API error, please try again in a few minutes."

    try:
        for day in weather['daily']:
            day['day'] = (datetime.utcfromtimestamp(day['dt']) + timedelta(seconds=weather['timezone_offset'])).strftime("%A")
        say(u"\x02{location}\x0F: ".format(location=geo['formatted_address']) +
            u". ".join([u"\x02{day}\x0F: L {temp[min]:.0f}\u00b0F, H {temp[max]:.0f}\u00b0F, {weather[0][description]}".format(**day)
            for day in weather['daily'][0:7]]))
    except:
        return "Error: unable to find weather data for location."

