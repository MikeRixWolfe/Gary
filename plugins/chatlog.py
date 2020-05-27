import datetime
import time
from sqlite3 import OperationalError
from util import hook, text, timesince, tokenize, web


@hook.command('l')
@hook.command
def last(inp, nick='', chan='', bot=None, db=None, say=None):
    """l[ast] <phrase> - Finds the last occurence of a phrase."""
    try:
        row = db.execute("select time, chan, nick, msg, uts from logfts where logfts match ? and (msg not like '!%' and msg not like ';%' and msg not like '.%') and cast(uts as decimal) < ? order by cast(uts as decimal) desc limit 1",
            (tokenize.build_query(inp), (time.time() - 1))).fetchone()
    except OperationalError:
        return "Error: must contain one inclusive match clause (+/=)."

    if row:
        _time, _chan, _nick, _msg, _uts = row

        if bot.config.get("logviewer_url"):
            log_url = web.try_googl(bot.config["logviewer_url"].format(_chan.strip('#'), *_time.split()))
        else:
            log_url = ''

        say('{} last said "{}" in {} on {} ({} ago) {}'.format(_nick, _msg, _chan,
            _time.split(' ')[0], timesince.timesince(float(_uts)), log_url).strip())
    else:
        say("Never!")


@hook.command('f')
@hook.command
def first(inp, chan='', bot=None, db=None, say=None):
    """f[irst] <phrase> - Finds the first occurence of a phrase."""
    try:
        row = db.execute("select time, chan, nick, msg, uts from logfts where logfts match ? and (msg not like '!%' and msg not like ';%' and msg not like '.%') limit 1",
            (tokenize.build_query(inp), )).fetchone()
    except OperationalError:
        return "Error: must contain one inclusive match clause (+/=)."

    if row:
        _time, _chan, _nick, _msg, _uts = row

        if bot.config.get("logviewer_url"):
            log_url = web.try_googl(bot.config["logviewer_url"].format(_chan.strip('#'), *_time.split()))
        else:
            log_url = ''

        say('{} first said "{}" in {} on {} ({} ago) {}'.format(_nick, _msg, _chan,
            _time.split(' ')[0], timesince.timesince(float(_uts)), log_url).strip())
    else:
        say("Never!")


@hook.command
def said(inp, chan='', db=None, say=None):
    """said <phrase> - Finds users who has said a phrase."""
    try:
        rows = db.execute("select distinct nick from logfts where logfts match ? and (msg not like '!%' and msg not like ';%' and msg not like '.%') order by nick",
            (tokenize.build_query(inp), )).fetchall()
        rows = ([row[0] for row in rows] if rows else None)
    except OperationalError:
        return "Error: must contain one inclusive match clause (+/=)."

    if rows:
        out = 'Said by '
        while rows:
            if len(out) + len(rows[0]) + len(str(len(rows))) < 450:
                out += rows.pop(0) + ", "
            else:
                break
        if rows:
            out += "{} others".format(len(rows))
        say(text.rreplace(out.strip(', '), ', ', ', and ', 1))
    else:
        say("No one!")

@hook.command
def rotw(inp, chan='', db=None, say=None):
    """rotw <phrase> - Displays the royalty of the word."""
    try:
        total = db.execute('select count(1) from logfts where logfts match ?',
            (tokenize.build_query(inp), )).fetchone()
        total = total[0] if total else None

        rows = db.execute("select distinct lower(nick), count(1) from logfts where logfts match ? group by lower(nick) order by count(1) desc limit 10",
            (tokenize.build_query(inp), )).fetchall()
    except OperationalError:
        return "Error: must contain one inclusive match clause (+/=)."

    if rows and total:
        out = []
        suffixes = {1: 'st', 2: 'nd', 3: 'rd'}
        for i, row in enumerate(rows):
            out.append('{}{}: {} {:,d} uses ({:.2%})'.format(i + 1,
                suffixes.get(i + 1, 'th'), row[0], row[1], float(row[1])/total))
        say('There are {:,d} uses of "{}". {}'.format(total, inp, ', '.join(out)))
    else:
        say("No one!")

