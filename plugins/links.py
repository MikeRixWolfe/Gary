import re
from datetime import datetime
from urllib2 import urlopen
from util import hook, http, web

html_re = r'https?://[^\s<>"]+|www\.[^\s<>"]+'

skipurls = ["youtube", "youtu.be", "rd.io", "rdio", "reddit", "spotify",
            "open.spotify.com", "steam"]


def prep_url(url):
    if not url.startswith('//') and '://' not in url:
        url = 'http://' + url

    try:
        url = urlopen(url).url
    except:
        pass

    return url


def get_title(url):
    try:
        request_url = http.get_html(url)
        titleget = request_url.xpath('//title/text()')[0]
        return unicode(titleget.strip()) or "No Title"
    except http.HTTPError as e:
        return "{} {}".format(e.code, e.msg)
    except:
        return "No Title"


@hook.regex(html_re, re.I)
def readtitle(match, say=None, nick=None):
    purl = match.group()

    if any(word in purl for word in skipurls):
        return

    say(u"{} - {}".format(web.try_googl(purl), get_title(prep_url(purl))))


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

    say("{} - {}".format(web.try_googl(url), get_title(prep_url(url))))


@hook.command(autohelp=False)
def linkdump(inp, chan="", say="", db=None):
    """.linkdump - Gets today's links dumped in channel."""
    today = datetime.today()
    period = float(datetime(today.year, today.month, today.day).strftime('%s'))
    rows = db.execute("select nick, msg, time from log where uts >= ? and chan = ? and " \
        "(msg like '%http://%' or msg like '%https://%' or msg like '%www.%')",
        (period, chan)).fetchall()

    if not rows:
        return "No links yet today (beginning with 'http')"

    links = [u"via {} [{}]: {} - {}".format(row[0],
        re.search(r'(\d+\:\d+:\d+)', row[2]).group(0),
        web.try_googl(re.search(html_re, row[1]).group(0)),
        get_title(prep_url(re.search(html_re, row[1]).group(0))))
        for row in rows]

    say("Today's link dump: " + web.haste('\n'.join(links), 'txt'))

