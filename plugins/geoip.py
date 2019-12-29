import re
from util import hook, http

formats = [
    "{ip} seems to be located in {city}, {region_name} in {country_name}",
    "{ip} seems to be located in {city} in {country_name}",
    "{ip} seems to be located in {region_name} in {country_name}",
    "{ip} seems to be located in {country_name}",
    "Unable to locate geolocation information for the given location"
]


def fformat(args):
    """find format string for args based on number of matches"""
    def match():
        for f in formats:
            try:
                yield f.format(**args), len(re.findall(r'(\{.*?\})',f))
            except:
                pass

    return max(dict(match()).iteritems(), key=lambda x: (x[1], len(x[0])))[0]


@hook.api_key('ipapi')
@hook.command
def geoip(inp, api_key=None):
    """geoip <IP address> - Gets the location of an IP address."""
    url = "http://api.ipapi.com/%s" % (http.quote(inp.encode('utf8'), safe=''))

    try:
        data = http.get_json(url, access_key=api_key)
    except:
        return "I couldn't find %s" % inp

    return fformat(data).replace('in United', 'in the United')

