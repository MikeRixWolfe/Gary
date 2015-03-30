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
        return web.try_googl(url), title.strip() or "No Title"
    except http.HTTPError as e:
        return web.try_googl(url), "{} {}".format(e.code, e.msg)
    except:
        return web.try_googl(url), "No Title"


@hook.regex(html_re, re.I)
def readtitle(match, say=None, nick=None):
    purl = match.group()

    if any(word in purl for word in skipurls):
        return

    say(u"{} - {}".format(*get_info(purl)))


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

    say(u"{} - {}".format(*get_info(url)))


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

    links = [u"via {} [{}]: {} - {}".format(row[0],
        re.search(r'(\d+\:\d+:\d+)', row[2]).group(0),
        *get_info(re.search(html_re, row[1]).group(0)))
        for row in rows]

    say("Today's link dump: " + web.haste('\n'.join(links), 'txt'))

