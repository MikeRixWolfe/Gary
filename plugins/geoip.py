import re
from util import hook, http, web

formats = [
    "{ip} seems to be located in {city}, {region_name} in {country_name}",
    "{ip} seems to be located in {city} in {country_name}",
    "{ip} seems to be located in {region_name} in {country_name}",
    "{ip} seems to be located in {country_name}",
    "Unable to locate geolocation information for the given location"
]


def flatten_dict(d):
    def items():
        for key, value in d.items():
            if isinstance(value, dict):
                for subkey, subvalue in flatten_dict(value).items():
                    yield key + "_" + subkey, subvalue
            else:
                yield key, value

    return dict(items())


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
    """.geoip <host/IP> - Gets the location of <host/IP>."""
    url = "http://freegeoip.net/json/%s" % (http.quote(inp.encode('utf8'), safe=''))
    #url = "http://geoip.nekudo.com/api/%s" % (http.quote(inp.encode('utf8'), safe=''))

    try:
        data = http.get_json(url)
    except:
        return "I couldn't find %s" % inp

    data = flatten_dict(data)
    data = {k:v for k,v in data.items() if v}

    return fformat(data).replace('in United', 'in the United')

