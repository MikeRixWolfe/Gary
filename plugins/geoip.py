import re
from util import hook, http, web

formats = [
    "{traits[ip_address]} seems to be located in {city[names][en]}, {subdivisions[0][names][en]} in {country[names][en]}",
    "{traits[ip_address]} seems to be located in {city[names][en]} in {country[names][en]}",
    "{traits[ip_address]} seems to be located in {subdivisions[0][names][en]} in {country[names][en]}",
    "{traits[ip_address]} seems to be located in {country[names][en]}",
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


@hook.command
def geoip(inp):
    """.geoip <IP address> - Gets the location of an IP address."""
    url = "http://geoip.nekudo.com/api/%s/full" % (http.quote(inp.encode('utf8'), safe=''))

    try:
        data = http.get_json(url)
    except:
        return "I couldn't find %s" % inp

    return fformat(data).replace('in United', 'in the United')

