import mimetypes
import time
import re
from datetime import datetime
from util import hook, http, web

link_re = r'https?:\/\/(?:www\.)?([^: \/]+\.[^: \/]+)(?::\d+)?\/?\S*'
domain_re = r'^.*?([^\/\.]+(?:\.[^\/\.]+)?)$'

skipurls = ["youtube.com", "youtu.be", "reddit.com", "spotify.com", "noxd.co",
            "steampowered.com", "imgur.com", "j.mp", "goo.gl", "worf.co", "redd.it",
            "is.gd", "bit.ly", "tinyurl.com", "twitter.com", "hastebin.com", "hasteb.in"]


def db_init(db):
    db.execute("create table if not exists links(time, server, chan, nick, user,"
               " link, slink, title, uts, primary key(time, server, chan, nick))")
    db.commit()


def log_link(db, server, chan, nick, user, link, slink, title):
    db.execute("insert into links(time, server, chan, nick, user, link, slink, title, uts)"
               " values(?, lower(?), lower(?), lower(?), lower(?), ?, ?, ?, ?)",
               (datetime.now(), server, chan, nick, user, link, slink, title, time.time()))
    db.commit()


def get_linkdump(db, server, chan, period, raw=False):
    q = "select nick, {}, title, time from links".format('link' if raw else 'slink')
    rows = db.execute(q + " where server = lower(?) and chan = lower(?) and uts >= ?",
                      (server, chan, period)).fetchall()
    return rows or None


def get_info(url):
    if not url.startswith('//') and '://' not in url:
        url = 'http://' + url

    try:
        mimetype, encoding = mimetypes.guess_type(url)
        if mimetype and any(mimetype.startswith(t) for t in ['video', 'audio', 'image']):
            return web.try_googl(url), None

        title = http.get_title(url)
        title = u' '.join(re.sub(u'\r|\n', u' ', title).split()).strip('| ')

        return web.try_googl(url), title or None
    except Exception as e:
        return web.try_googl(url), None


@hook.regex(link_re, re.I)
def readtitle(match, say=None, db=None, input=None):
    db_init(db)
    url = match.group()
    surl, title = get_info(url)
    domain = re.match(domain_re, match.group(1)).group(1)

    try:
        log_link(db, input.server, input.chan, input.nick,
            input.user, url, surl, title or domain)
    except Exception as e:
        print(">>> u'Error logging link: {} :{}'".format(e, chan))

    if domain not in skipurls:
        say(surl + (u" - {}".format(title) if title else ""))
    else:
        print(u">>> Link skipped: {}".format(domain))


@hook.command
def shorten(inp, chan='', server='', say=None, db=None):
    """shorten <link|that> - Shortens a link, or the last link that was said."""
    if inp == 'that':
        try:
            inp = db.execute("select link from links where server = ? and" \
                "chan = ? order by uts desc limit 1", (server, chan)).fetchone()[0]
        except:
            return "Unable to shorten last link."

    url, title = get_info(inp)
    say(url + (u" - {}".format(title) if title else ""))


@hook.command(autohelp=False)
def linkdump(inp, chan='', server='', say=None, db=None):
    """linkdump [-l] - Gets today's links dumped in channel; -l for unshortened links."""
    today = datetime.today()
    period = float(datetime(today.year, today.month, today.day).strftime('%s'))
    rows = get_linkdump(db, server, chan, period, (True if inp == '-l' else False))

    if not rows:
        return "No links yet today (beginning with 'http')"

    links = []
    for row in rows:
        nick, slink, title, time = row
        links.append(u"via {} [{}]: {}".format(nick,
            re.search(r'(\d+\:\d+:\d+)', time).group(0),
            (slink + (u" - {}".format(title) if title else ""))))

    say("Today's link dump: " + web.haste(u'\n'.join(links).encode('utf-8'), 'txt'))

