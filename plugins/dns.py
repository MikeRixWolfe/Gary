'''
dns.py - written by MikeFightsBears 2013
'''

from util import hook
import socket

@hook.command
def dns(inp):
    "dns <domain> - resolves IP of Domain"
    socket.setdefaulttimeout(5)
    ip = socket.gethostbyname(inp)
    return "%s resolves to %s" % (inp, ip)
    
@hook.command
def rdns(inp):
    "rdns <ip> - resolves Hostname of IP"
    socket.setdefaulttimeout(5)
    domain = socket.gethostbyaddr(inp)
    return "%s resolves to %s" % (inp, domain)
    
