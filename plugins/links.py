import re
from datetime import datetime
from urllib2 import urlopen
from util import hook, http, web

html_re = r'https?://(?:www\.)?([^/]+)/?\S*'

skipurls = ["youtube.com", "youtu.be", "rd.io", "rdio.com", "reddit.com",
            "spotify.com", "steam.com", "imgur.com", "j.mp", "goo.gl"]


def get_info(url):
    if not url.startswith('//') and '://' not in url:
        url = 'http://' + url
    try:
        title = http.get_title(url)
        title = u' '.join(re.sub(u'\r|\n', u' ', title).split()).strip('| ')
        return web.try_googl(url), title or None
    except:
        return web.try_googl(url), None


@hook.regex(html_re, re.I)
def readtitle(match, say=None):
    if http.urlparse.urlparse(match.group()).hostname.strip('www.') in skipurls:
        print u">>> Link skipped: {}".format(match.group(1))
        return

    url, title = get_info(match.group())
    if (title or len(url) < len(match.group())):
        say(url + (u" - {}".format(title) if title else ""))


@hook.command
def shorten(inp, chan='', say=None, db=None):
    """.shorten <link|that> - Shortens a link, or the last link that was said."""
    if inp == 'that':
        try:
            row = db.execute("select msg from links where chan = ? " \
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
    rows = db.execute("select nick, msg, time from links where uts >= ? and chan = ? ",
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

