"""
weather.py - written by MikeFightsBears 2013
"""

import json
import urllib2
import lxml.etree
from util import hook, http
#from xml.dom import minidom

wurl = 'http://xml.weather.yahoo.com/forecastrss?p=%s'
wser = 'http://xml.weather.yahoo.com/ns/rss/1.0'


@hook.command
@hook.command('w')
def weather(inp):
    ".w[eather] <zip code> - Gets the current weather conditions for a given zipcode"
    url = wurl % inp + '&u=f'
    parsed = http.get_xml(url)
    if len(parsed) != 1:
        return "Error parsing Yahoo Weather API, please try again later..."

    doc = lxml.etree.parse(urllib2.urlopen(url)).getroot()

    location = doc.xpath('*/yweather:location',
                         namespaces={'yweather': 'http://xml.weather.yahoo.com/ns/rss/1.0'})
    conditions = doc.xpath('*/*/yweather:condition',
                           namespaces={'yweather': 'http://xml.weather.yahoo.com/ns/rss/1.0'})
    wind = doc.xpath('*/yweather:wind',
                     namespaces={'yweather': 'http://xml.weather.yahoo.com/ns/rss/1.0'})
    atmosphere = doc.xpath('*/yweather:atmosphere',
                           namespaces={'yweather': 'http://xml.weather.yahoo.com/ns/rss/1.0'})
    astronomy = doc.xpath('*/yweather:astronomy',
                          namespaces={'yweather': 'http://xml.weather.yahoo.com/ns/rss/1.0'})

    try:
        condition = conditions[0]
    except IndexError:
        return "City not found"
    # there HAS to be a way to clean this crap up
    return "\x02" + location[0].items()[0][1] + \
        ", " + \
        location[0].items()[1][1] + \
        "\x0F: " + \
        conditions[0].items()[2][1] + \
        "*F and " + \
        conditions[0].items()[0][1] + \
        ", wind chill " + \
        wind[0].items()[0][1] + \
        "*F (" + \
        wind[0].items()[2][1] + \
        "MPH " + \
        cards.get(int(wind[0].items()[1][1]), cards[min(cards.keys(), key=lambda k: abs(k - int(wind[0].items()[1][1])))]) + \
        "); Humidity at " + \
        atmosphere[0].items()[0][1] + \
        "%, visibility at " +  \
        atmosphere[0].items()[1][1] + \
        " miles, barometric pressure is " + \
        atmosphere[0].items()[2][1] + \
        "."
        #"(delta " + atmosphere[0].items()[3][1] + ")"


@hook.command('f')
@hook.command
def forecast(inp):
    ".f[orecast] <zip code> - gets the current weather conditions for a given zipcode"
    url = wurl % inp + '&u=f'
    parsed = http.get_xml(url)

    if len(parsed) != 1:
        return "Error parsing Yahoo Weather API, please try again later..."
    doc = lxml.etree.parse(urllib2.urlopen(url)).getroot()

    location = doc.xpath('*/yweather:location',
                         namespaces={'yweather': 'http://xml.weather.yahoo.com/ns/rss/1.0'})
    forecast = doc.xpath('*/*/yweather:forecast',
                         namespaces={'yweather': 'http://xml.weather.yahoo.com/ns/rss/1.0'})
    try:
        fc = forecast[0]
    except IndexError:
        return "City not found"

    # again, there MUST be a better way!
    forecast_string = "Forecast for \x02" + \
        location[0].items()[0][1] + ", " + location[0].items()[1][1] + "\x0F: "
    for f in forecast:
        forecast_string += "\x02" + f.items()[0][1] + ", " + f.items()[1][1] + "\x0F: L " + \
            f.items()[2][1] + "*F, H " + f.items()[3][1] + \
            "*F, and "  + \
            f.items()[4][1] + "; "
    return forecast_string

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
