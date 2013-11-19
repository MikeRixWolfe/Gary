"""
weather.py written by MikeFightsBears 2013
"""

import urllib2
import lxml.etree
from util import hook, http
#from xml.dom import minidom

wurl = 'http://xml.weather.yahoo.com/forecastrss?p=%s'
wser = 'http://xml.weather.yahoo.com/ns/rss/1.0'

@hook.command
@hook.command('w')
def weather(inp):
    ".w[eather] <zip code> - gets the current weather conditions for a given zipcode"
    
    url = wurl % inp +'&u=f'
    
    parsed = http.get_xml(url)

    if len(parsed) != 1:
	return "error getting weather info"

    doc = lxml.etree.parse( urllib2.urlopen(url) ).getroot()
    
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
        condition=conditions[0]
    except IndexError:
        return "City not found"
    #there HAS to be a way to clean this crap up
    return location[0].items()[0][1] + ", " + location[0].items()[1][1] + ": " + conditions[0].items()[2][1] + "*F and " + conditions[0].items()[0][1] + "; wind chill " + wind[0].items()[0][1] + "*F, speed " + wind[0].items()[2][1] + "MPH, direction " + wind[0].items()[1][1] + "* from N; humidity at " + atmosphere[0].items()[0][1] + "%, visibility at " +  atmosphere[0].items()[1][1] + " miles, barometric pressure is " + atmosphere[0].items()[2][1] + "(delta " + atmosphere[0].items()[3][1] + ")"  

    
@hook.command('f')
@hook.command
def forecast(inp):
    ".f[orecast] <zip code> - gets the current weather conditions for a given zipcode"  

    url = wurl % inp +'&u=f' 
    parsed = http.get_xml(url) 

    if len(parsed) != 1: 
	return "error getting weather info"   

    doc = lxml.etree.parse( urllib2.urlopen(url) ).getroot()
    
    location = doc.xpath('*/yweather:location',
	namespaces={'yweather': 'http://xml.weather.yahoo.com/ns/rss/1.0'})
    forecast = doc.xpath('*/*/yweather:forecast',
	namespaces={'yweather': 'http://xml.weather.yahoo.com/ns/rss/1.0'})
    try:
	fc=forecast[0]
    except IndexError:
	return "City not found"

    #again, there MUST be a better way!
    forecast_string = "Forecast for " + location[0].items()[0][1] + ", " + location[0].items()[1][1] + ": "
    for f in forecast:
	forecast_string += f.items()[0][1] + ", " + f.items()[1][1] + ": low of " + f.items()[2][1] + "*F, high of " + f.items()[3][1] + "*F, and "  + f.items()[4][1] + "; "
    return forecast_string
