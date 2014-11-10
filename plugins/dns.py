import re
import socket
from util import hook


@hook.command
def dns(inp):
    """.dns <ip|domain> - Resolves IP of Domain or vice versa."""
    try:
        socket.setdefaulttimeout(15)
        if not re.match(r'\d+\.\d+\.\d+\.\d+', inp):
            out = socket.gethostbyname(inp)
        else:
            out = socket.gethostbyaddr(inp)[0]
        return "%s resolves to %s" % (inp, out)
    except:
        return "I could not find {}".format(inp)
