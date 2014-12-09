import socket
from util import hook, http


@hook.command
def isup(inp):
    """.isup <site> - Checks if a site is up or not."""
    if not inp.startswith('//') and '://' not in inp:
        inp = '//' + inp
    urlp = http.urlparse.urlparse(inp, 'http')
    url = "%s://%s" % (urlp.scheme, urlp.netloc)

    try:
        page = http.open(url)
        code = page.getcode()
    except http.HTTPError as e:
        code = e.code
    except socket.timeout as e:
        code = 'Socket Timeout'
    except Exception as e:
        return "Huh? That doesn't look like a site on the interwebs."

    if code == 200:
        return "It's just you. {} is \x02\x033up\x02\x0f.".format(url)
    else:
        return "It's not just you. {} looks \x02\x034down\x02\x0f from here ({})".format(url, code)
