import re
from util import hook, http, web

formats = [
    "{ip} seems to be located in {locality}, {administrative_area_level_1} in {country}",
    "{ip} seems to be located in {locality} in {country}",
    "{ip} seems to be located in {administrative_area_level_1} in {country}",
    "{ip} seems to be located in {country}",
    "Unable to locate geolocation information for the given location"
]


def flatten_dict(d):
    """turn nested dictionaries into a flat dictionary"""
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


@hook.api_key('google')
@hook.command
def geoip(inp, api_key=None):
    """.geoip <IP address> - Gets the location of an IP address."""
    if not isinstance(api_key, dict) or any(key not in api_key for key in
            ('access', 'cx')):
        return "Error: API keys not set."

    ip_url = "http://geoip.nekudo.com/api/{}".format(http.quote(inp.encode('utf8'), safe=''))
    loc_url = "https://maps.googleapis.com/maps/api/geocode/json"

    try:
        data = http.get_json(ip_url)
    except:
        return "I couldn't find {}".format(inp)

    data = flatten_dict(data)
    data = {k:v for k,v in data.items() if v}
    loc = "{location_latitude},{location_longitude}".format(**data)

    params = {
        'key': api_key['access'],
        'latlng': loc
    }

    try:
        data = http.get_json(loc_url, query_params=params)
    except:
        return "I couldn't lookup location data for {}".format(inp)

    data = dict(zip([[t for t in d['types'] if t != 'political'][0] for d in data['results'][0]['address_components'] if 'political' in d['types']],
        [d['long_name'] for d in data['results'][0]['address_components'] if 'political' in d['types']]))
    data['ip'] = inp

    return fformat(data).replace('in United', 'in the United')

