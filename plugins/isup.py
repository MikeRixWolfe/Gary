import urlparse
import socket
from util import hook, http, urlnorm


@hook.command
def isup(inp):
    ".isup <site> - uses isup.me to see if a site is up or not"

    # slightly overcomplicated, esoteric URL parsing
    scheme, auth, path, query, fragment = urlparse.urlsplit(inp.strip())

    domain = auth.encode('utf-8') or path.encode('utf-8')
    url = urlnorm.normalize(domain, assume_scheme="http")

    try:
        soup = http.get_soup('http://isup.me/' + domain, timeout = 15)
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
            return 'Error: %s: %s' % (e.code, errors[e.code])
        return 'Error: %s' % e.code
    except socket.timeout as e:
        return "Error: %s" % e
    except:
        return "Could not get status."

    content = soup.find('div').text.strip()

    if "not just you" in content:
        return "It's not just you. {} looks \x02\x034down\x02\x0f from here!".format(url)
    elif "is up" in content:
        return "It's just you. {} is \x02\x033up\x02\x0f.".format(url)
    else:
        return "Huh? That doesn't look like a site on the interwebs."
