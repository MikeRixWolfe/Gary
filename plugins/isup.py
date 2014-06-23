import socket
from util import hook, http, urlnorm


@hook.command
def isup(inp):
    ".isup <site> - Checks if a site is up or not"

    # slightly overcomplicated, esoteric URL parsing
    scheme, auth, path, query, fragment = http.urlparse.urlsplit(inp.strip())

    domain = auth.encode('utf-8') or path.encode('utf-8')
    url = urlnorm.normalize(domain, assume_scheme="http")

    try:
        page = http.open(url)
    except http.HTTPError as e:
        errors = {400: 'Bad Request (ratelimited?)',
                  401: 'Unauthorized Request',
                  403: 'Forbidden',
                  404: 'Not Found',
                  500: 'Internal Server Error',
                  502: 'Bad Gateway',
                  503: 'Service Unavailable',
                  410: 'Resource is Gone'}
        if e.code in errors:
            return 'Error: %s [%s]' % (errors[e.code], e.code)
        return 'Error: %s' % e.code
    except socket.timeout as e:
        return "Error: %s" % e
    except:
        return "Could not get status."

    if page.getcode() != 200:
        return "It's not just you. {} looks \x02\x034down\x02\x0f from here!".format(url)
    elif page.getcode() == 200:
        return "It's just you. {} is \x02\x033up\x02\x0f.".format(url)
    else:
        return "Huh? That doesn't look like a site on the interwebs."
