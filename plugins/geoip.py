import os
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

    return fformat(data)


@hook.command
def whereis(inp):
    """.whereis <user> - Gets the IP and location of a system user."""
    cmd = "w -hs %s | awk '{print $3}' | sort | head -n 1" % inp.split()[0]
    ip = os.popen(cmd).read().strip()
    if ip:
        octets = re.match(r'.*?(\d+)\W{1}(\d+)\W{1}(\d+)\W{1}(\d+).*', ip)
        if octets:
            ip = ".".join(octets.groups())
            out = inp.split()[0] + " (" + ip + ")"
            if octets.group(1) == "10":
                out += " is on the local network via wifi"
            elif octets.group(1) == "192":
                out += " is on the local network via copper"
            else:
                out += geoip(ip)
                return out.replace(ip+' ',' ')
        else:
            out = "Sorry, I couldn't locate that user."
    else:
        out = "Sorry, that user doesn't appear to be logged in."
    return out

