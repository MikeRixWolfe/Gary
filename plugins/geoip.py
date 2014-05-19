import os
import re
from util import hook, http, web


@hook.command
def geoip(inp):
    ".geoip <host/ip> - Gets the location of <host/ip>"

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
    ".whereis <user> - gets the ip and location of a system user"
    cmd = "w -hs | awk '{print $1 \" \" $3}' | grep \"%s\" | tail -n 1 | awk '{print $2}'" % inp.strip().split()[0]
    ip = os.popen(cmd).read().strip()
    if ip:
        if not ip[0].isdigit():
            ip = "localhost"
            content = None
        else:
            url = "http://freegeoip.net/json/%s" % \
                  (http.quote(ip.encode('utf8'), safe=''))
            try:
                content = http.get_json(url)
            except:
                content = None
        out = inp.strip() + " (" + ip + ")"
        if content:
            out = out + " seems to be located in " + content["city"] + \
                ", " + content["region_name"] + " " + \
                content["zipcode"] + " in " + content["country_name"]
        else:
            out = out + " is located somewhere in the universe."
    else:
        out = "Sorry, I couldn't find that user."
    return out


@hook.command
def map(inp):
    ".map <place>|<origin> to <destination> - Gets a Map of place or route from Google Maps"
    return web.try_googl('https://www.google.com/maps/?q=' +
        '+'.join(inp.split(' ')))
