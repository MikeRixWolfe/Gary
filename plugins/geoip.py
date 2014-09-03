import os
import re
from util import hook, http, web


@hook.command
def geoip(inp):
    """.geoip <host/IP> - Gets the location of <host/IP>."""
    url = "http://freegeoip.net/json/%s" % \
          (http.quote(inp.encode('utf8'), safe=''))

    try:
        content = http.get_json(url)
    except:
        return "I couldn't find %s" % inp

    if content["city"] or content["region_name"] or content["country_name"]:
        if content["country_name"] == 'Reserved':
            out = inp + " is reserved."
        else:
            out = inp + " seems to be located "
            if content["city"] and content["region_name"]:
                out += "in %s, %s" % (content["city"], content["region_name"])
            elif content["city"]:
                out += "in %s" % content["city"]
            elif content["region_name"]:
                out += "in %s" % content["region_name"]
            else:
                out += "somewhere"
            if content["country_name"]:
                out += " in %s" % content["country_name"]
            else:
                out += ", somewhere in the world"
    else:
        out = "I couldn't find any geographical information on %s" % inp

    return out


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
                url = "http://freegeoip.net/json/%s" % \
                    (http.quote(ip.encode('utf8'), safe=''))
                try:
                    content = http.get_json(url)
                except:
                    content = None
                if content:
                    out += " seems to be located in " + content["city"] + \
                            ", " + content["region_name"] + \
                            " in " + content["country_name"]
                else:
                    out += " is located somewhere in the universe."
        else:
            out = "Sorry, I couldn't locate that user."
    else:
        out = "Sorry, that user doesn't appear to be logged in."
    return out


@hook.command
def map(inp):
    """.map <place>|<origin to destination> - Gets a Map of place or route from Google Maps."""
    return web.try_googl('https://www.google.com/maps/?q=' +
        http.quote_plus(inp))
