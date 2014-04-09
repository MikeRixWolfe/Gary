from util import hook
import socket


@hook.command
def dns(inp):
    "dns <domain> - resolves IP of Domain"
    try:
        socket.setdefaulttimeout(15)
        ip = socket.gethostbyname(inp)
        return "%s resolves to %s" % (inp, ip)
    except:
        return "I could not find {}".format(inp)


@hook.command
def rdns(inp):
    "rdns <ip> - resolves Hostname of IP"
    try:
        socket.setdefaulttimeout(5)
        domain = socket.gethostbyaddr(inp)
        return "%s resolves to %s" % (inp, domain)
    except:
        return "I could not find {}".format(inp)
