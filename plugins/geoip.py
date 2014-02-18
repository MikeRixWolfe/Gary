"""
geoip.py: written by MikeFightsBears 2013
"""

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

    out = inp + " seems to be located in " + content["city"] + \
        ", " + content["region_name"] + " " + \
        content["zipcode"] + " in " + content["country_name"]
    return out


@hook.command
def whereis(inp):
    ".whereis <user> - gets the ip and location of a system user"
    cmd = "w -hs | awk '{print $1 \" \" $3}' | grep \"%s\" | tail -n 1 | awk '{print $2}'" % inp.strip(
        ' ')
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
    ".map <origin> to <destination> - Generates Google Maps route"
    if not re.match(r'^(.+)?(\ to\ )(.+)', inp):
        return map.__doc__
    else:
        return web.try_isgd('https://www.google.com/maps/?q=' +
                            '+'.join(inp.split(' ')))
