import socket
from util import hook, http


@hook.command
def isup(inp):
    """isup <site> - Checks if a site is up or not."""
    url = 'http://' + inp if '://' not in inp else inp

    try:
        page = http.open(url)
        code = page.getcode()
    except http.HTTPError as e:
        code = e.code
    except socket.timeout as e:
        code = 'Socket Timeout'
    except Exception as e:
        code = 'DNS Not Resolved'

    if code == 200:
        return "It's just you. {} is \x02\x033up\x02\x0f.".format(url)
    else:
        return "It's not just you. {} looks \x02\x034down\x02\x0f from here ({})".format(url, code)
