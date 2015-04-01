import re
from datetime import datetime
from urllib2 import urlopen
from util import hook, http, web

html_re = r'https?://[^\s<>"]+|www\.[^\s<>"]+'

skipurls = ["youtube", "youtu.be", "rd.io", "rdio", "reddit", "spotify",
            "open.spotify.com", "steam", "imgur", "i.imgur"]


def get_info(url):
    if not url.startswith('//') and '://' not in url:
        url = 'http://' + url
    try:
        request_url = urlopen(url)
        url = request_url.url
        title = http.html.fromstring(request_url.read()).xpath('//title/text()')[0]
        title = u' '.join(re.sub(u'\r|\n', u' ', title).split())
        return web.try_googl(url), title or None
    except http.HTTPError as e:
        return web.try_googl(url), "[{} {}]".format(e.code, e.msg)
    except:
        return web.try_googl(url), None


@hook.regex(html_re, re.I)
def readtitle(match, say=None, nick=None):
    purl = match.group()
    if any(word in purl for word in skipurls):
        return

    url, title = get_info(purl)
    if (title or len(url) < len(purl)):
        say(url + (u" - {}".format(title) if title else ""))


@hook.command
def shorten(inp, chan='', say=None, db=None):
    # Useful if readtitle is disabled
    if inp == 'that':
        try:
            row = db.execute("select msg from log where chan = ? and " \
                "(msg like '%http://%' or msg like '%https://%' or msg like '%www.%') " \
                "order by uts desc limit 1", (chan,)).fetchone()
            url = re.search(html_re, row[0]).group()
        except:
            return "Unable to shorten last link."
    else:
        url = inp

    url, title = get_info(url)
    say(url + (u" - {}".format(title) if title else ""))


@hook.singlethread
@hook.command(autohelp=False)
def linkdump(inp, chan="", say="", db=None):
    """.linkdump - Gets today's links dumped in channel."""
    say("Generating today's linkdump...")
    today = datetime.today()
    period = float(datetime(today.year, today.month, today.day).strftime('%s'))
    rows = db.execute("select nick, msg, time from log where uts >= ? and chan = ? and " \
        "(msg like '%http://%' or msg like '%https://%' or msg like '%www.%')",
        (period, chan)).fetchall()

    if not rows:
        return "No links yet today (beginning with 'http')"

    links = []
    for row in rows:
        who, stamp = row[0], re.search(r'(\d+\:\d+:\d+)', row[2]).group(0)
        url, title = get_info(re.search(html_re, row[1]).group(0))
        links.append(u"via {} [{}]: {}".format(who, stamp,
            (url + (u" - {}".format(title) if title else ""))))

    say("Today's link dump: " + web.haste(u'\n'.join(links).encode('utf-8'), 'txt'))

