import datetime
import time
from util import hook, timesince, text, web


@hook.command('l')
@hook.command
def last(inp, nick='', chan='', input=None, db=None, say=None):
    """last <phrase> - Finds the last occurence of a phrase."""
    row = db.execute('select time, chan, nick, msg, uts from logfts where logfts match ? and uts < ? order by cast(uts as decimal) desc limit 1',
        ('msg:"{}"* AND chan:{}'.format(inp, chan.strip('#')), (time.time() - 1))).fetchone()

    if row:
        xtime, xchan, xnick, xmsg, xuts = row
        say("%s last said \"%s\" in %s on %s (%s ago)" %
            (xnick, xmsg, xchan, xtime.split('.')[0], timesince.timesince(int(xuts))))
    else:
        say("Never!")


@hook.command
def first(inp, chan='', input=None, db=None, say=None):
    """first <phrase> - Finds the first occurence of a phrase."""
    row = db.execute('select time, chan, nick, msg, uts from logfts where logfts match ? order by cast(uts as decimal) asc limit 1',
        ('msg:"{}"* AND chan:{} NOT uts:0'.format(inp, chan.strip('#')), )).fetchone()

    if row:
        xtime, xchan, xnick, xmsg, xuts = row
        say("%s first said \"%s\" in %s on %s (%s ago)" %
            (xnick, xmsg, xchan, xtime.split('.')[0], timesince.timesince(int(xuts))))
    else:
        say("Never!")


@hook.command
def said(inp, chan='', input=None, db=None, say=None):
    """said <phrase> - Finds users who has said a phrase."""
    rows = db.execute('select distinct nick from logfts where logfts match ? order by nick',
        ('msg:"{}"* AND chan:{}'.format(inp, chan.strip('#')), )).fetchall()
    rows = ([row[0] for row in rows] if rows else None)

    if rows:
        out = ''
        while rows:
            if len(out) + len(rows[0]) + len(str(len(rows))) < 440:
                out += rows.pop(0) + ", "
            else:
                break
        if rows:
            out += "{} others".format(len(rows))
        out = text.rreplace(out.strip(', '), ', ', ', and ', 1)
        say(out + ' have said "{}"'.format(inp))
    else:
        say("No one!")

@hook.command
def rotw(inp, chan='', input=None, db=None, say=None):
    """rotw <phrase> - Displays the royalty of the word."""
    total = db.execute('select count(1) from logfts where logfts match ?',
        ('msg:"{}"* AND chan:{}'.format(inp, chan.strip('#')), )).fetchone()
    total = total[0] if total else None

    rows = db.execute('select distinct nick, count(1) from logfts where logfts match ? group by nick order by count(1) desc limit 10',
        ('msg:"{}"* AND chan:{}'.format(inp, chan.strip('#')), )).fetchall()

    if rows:
        out = []
        suffixes = {1: 'st', 2: 'nd', 3: 'rd'}
        for i, row in enumerate(rows):
            out.append('{}{}: {} {} uses ({:.2%})'.format(i + 1,
                suffixes.get(i + 1, 'th'), row[0], row[1], float(row[1])/total))
        say('There are {} uses of "{}" in {}. {}'.format(total, inp, chan, ', '.join(out)))
    else:
        say("No one!")

