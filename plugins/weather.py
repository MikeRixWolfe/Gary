from datetime import date, datetime, timedelta
from util import hook, http


cards = { 0: "N", 22.5: "NNE", 45: "NE", 67.5: "ENE", 90: "E", 112.5: "ESE",
          135: "SE", 157.5: "SSE", 180: "S", 202.5: "SSW", 225: "SW", 257.5: "WSW",
          270: "W", 292.5: "WNW", 315: "NW", 337.5: "NNW", 360: "N" }

ww = { 0: "clear skies", 1: "mostly clear skies", 2: "partly cloudy skies", 3: "overcast skies", 45: "fog", 48: "depositing rime fog",
       51: "light drizzle", 53: "drizzle", 55: "heavy drizzle", 56: "light freezing drizzle", 57: "heavy freezing drizzle",
       61: "light rain", 63: "rain", 65: "heavy rain", 66: "light freezing rain", 67: "heavy freezing rain",
       71: "light snow", 73: "moderate snow", 75: "heavy snow", 77: "snow grains",
       80: "light rain showers", 81: "moderate rain showers", 82: "heavy rain showers", 85: "light snow showers", 86: "heavy snow showers",
       95: "thunderstorms", 96: "thunderstorms with hail", 99: "heavy thunderstorms with hail" }


def strftime(time):
    return datetime.fromtimestamp(time).strftime("%p %A").replace('AM', 'early').replace('PM', 'late')


@hook.api_key('google')
@hook.command('w')
@hook.command
def weather(inp, say=None, api_key=None):
    """w[eather] <zip code|location> - Gets the current weather conditions."""
    if api_key is None:
        return "Error: API key not set."

    try:
        geo_url = 'https://maps.googleapis.com/maps/api/geocode/json'
        params = {'key': api_key['access'], 'address': inp}
        geo = http.get_json(geo_url, query_params=params)['results'][0]
    except:
        return "Google Geocoding API error, please try again in a few minutes."

    try:
        meteo_url = 'https://api.open-meteo.com/v1/forecast'
        params = {'latitude': geo['geometry']['location']['lat'], 'longitude': geo['geometry']['location']['lng'],
            'current': 'temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m,wind_direction_10m,wind_gusts_10m',
            'temperature_unit': 'fahrenheit', 'wind_speed_unit': 'mph', 'precipitation_unit': 'inch', 'timezone': 'America/Chicago', 'timeformat': 'unixtime' }
        weather = http.get_json(meteo_url, query_params=params)
    except:
        return "Meteo API error, please try again in a few minutes."

    try:
        direction = cards.get(float(weather['current']['wind_direction_10m']),
            cards[min(cards.keys(), key=lambda k: abs(k - float(weather['current']['wind_direction_10m'])))])

        weather['current']['wind_gusts_10m'] = weather['current'].get('wind_gusts_10m', weather['current']['wind_speed_10m'] + 1)
        weather['current']['description'] = ww[weather['current']['weather_code']]

        # unique alerts preferring the highest priority, and nearest in the future
        alerts = [a for a in weather.get('alerts', []) if 'Watch' in a['event'] or ('Warning' in a['event'] and
            a['event'].replace('Warning', 'Watch') not in [x['event'] for x in weather.get('alerts', [])])]
        alerts = sorted([min(filter(lambda x: x['event'] == t, alerts), key=lambda x: x['start']) for t in
            set(a['event'] for a in alerts)], key=lambda x: x['start'])
        alerts = ', '.join(['\x02{}\x0F until \x02{}\x0F'.format(a['event'], strftime(a['end'])) for a in alerts])

        say(u"\x02{location}\x0F: {current[temperature_2m]:.0f}\u00b0F " \
            u"with {current[description]}, feels like {current[apparent_temperature]:.0f}\u00b0F, " \
            u"wind at {current[wind_speed_10m]:.0f} MPH ({current[wind_gusts_10m]:.0f} MPH gust) {direction}, " \
            u"humidity at {current[relative_humidity_2m]:.0f}%. {alert}".format(direction=direction,
            location=geo['formatted_address'], alert=alerts, **weather))
    except:
        return "Error: unable to find weather data for location."


@hook.api_key('google')
@hook.command('h')
@hook.command
def hourly(inp, say=None, api_key=None):
    """h[ourly] <zip code|location> - Gets the 10 hour weather forecast."""
    if api_key is None:
        return "Error: API key not set."

    try:
        geo_url = 'https://maps.googleapis.com/maps/api/geocode/json'
        params = {'key': api_key['access'], 'address': inp}
        geo = http.get_json(geo_url, query_params=params)['results'][0]
    except:
        return "Google Geocoding API error, please try again in a few minutes."

    try:
        meteo_url = 'https://api.open-meteo.com/v1/forecast'
        params = {'latitude': geo['geometry']['location']['lat'], 'longitude': geo['geometry']['location']['lng'],
            'hourly': 'temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m,wind_direction_10m,wind_gusts_10m',
            'temperature_unit': 'fahrenheit', 'wind_speed_unit': 'mph', 'precipitation_unit': 'inch', 'timezone': 'America/Chicago', 'timeformat': 'unixtime' }
        weather = http.get_json(meteo_url, query_params=params)
    except:
        return "Meteo API error, please try again in a few minutes."

    try:
        weather['hours'] = []
        for i, hour in enumerate(weather['hourly']['time']):
            if datetime.fromtimestamp(hour) >= datetime.now():
                weather['hours'].append({
                    'time': (datetime.utcfromtimestamp(weather['hourly']['time'][i]) + timedelta(seconds=weather['utc_offset_seconds'])).strftime("%-I%p"),
                    'temperature_2m': weather['hourly']['temperature_2m'][i],
                    'relative_humidity_2m': weather['hourly']['relative_humidity_2m'][i],
                    'apparent_temperature': weather['hourly']['apparent_temperature'][i],
                    'weather_code': weather['hourly']['weather_code'][i],
                    'wind_speed_10m': weather['hourly']['wind_speed_10m'][i],
                    'wind_direction_10m': weather['hourly']['wind_direction_10m'][i],
                    'wind_gusts_10m': weather['hourly']['wind_gusts_10m'][i],
                    'description': ww[weather['hourly']['weather_code'][i]]
                })

        say(u"\x02{location}\x0F: ".format(location=geo['formatted_address']) +
            u". ".join([u"\x02{time}\x0F: {temperature_2m:.0f}\u00b0F ({apparent_temperature:.0f}\u00b0F feel), {description}".format(**hour)
            for hour in weather['hours'][0:10]]))
    except:
        return "Error: unable to find weather data for location."


@hook.api_key('google')
@hook.command('fc')
@hook.command
def forecast(inp, say=None, api_key=None):
    """forecast/fc <zip code|location> - Gets the 7 day weather forecast."""
    if api_key is None:
        return "Error: API key not set."

    try:
        geo_url = 'https://maps.googleapis.com/maps/api/geocode/json'
        params = {'key': api_key['access'], 'address': inp}
        geo = http.get_json(geo_url, query_params=params)['results'][0]
    except:
        return "Google Geocoding API error, please try again in a few minutes."

    try:
        meteo_url = 'https://api.open-meteo.com/v1/forecast'
        params = {'latitude': geo['geometry']['location']['lat'], 'longitude': geo['geometry']['location']['lng'],
            'daily': 'temperature_2m_min,temperature_2m_max,apparent_temperature_min,apparent_temperature_max,weather_code',
            'temperature_unit': 'fahrenheit', 'wind_speed_unit': 'mph', 'precipitation_unit': 'inch', 'timezone': 'America/New_York', 'timeformat': 'unixtime' }
        weather = http.get_json(meteo_url, query_params=params)
    except:
        return "Meteo API error, please try again in a few minutes."

    try:
        weather['days'] = []
        for i, day in enumerate(weather['daily']['time']):
            if datetime.utcfromtimestamp(day) >= datetime.fromordinal(date.today().toordinal()):
                weather['days'].append({
                    'time': (datetime.utcfromtimestamp(weather['daily']['time'][i]) + timedelta(seconds=weather['utc_offset_seconds'])).strftime("%A"),
                    'temperature_2m_min': weather['daily']['temperature_2m_min'][i],
                    'temperature_2m_max': weather['daily']['temperature_2m_max'][i],
                    'apparent_temperature_min': weather['daily']['apparent_temperature_min'][i],
                    'apparent_temperature_max': weather['daily']['apparent_temperature_max'][i],
                    'weather_code': weather['daily']['weather_code'][i],
                    'description': ww[weather['daily']['weather_code'][i]]
                })

        say(u"\x02{location}\x0F: ".format(location=geo['formatted_address']) +
            u". ".join([u"\x02{time}\x0F: L {temperature_2m_min:.0f}\u00b0F, H {temperature_2m_max:.0f}\u00b0F, {description}".format(**day)
            for day in weather['days'][0:7]]))
    except:
        return "Error: unable to find weather data for location."

