import datetime
import time
from util import hook, timesince, text, web


@hook.command(autohelp=False)
def convo(inp, chan='', server='', say=None, db=None):
    """convo [# of lines] - Gets the last number of lines for the channel; defaults to 10."""
    num = int(inp) if inp.isdigit() and 1 <= int(inp) <= 50 else 10
    rows = db.execute('select time, nick, msg from logfts where logfts match ? order by uts desc limit ?',
        ('chan:{}'.format(chan.strip('#')), num)).fetchall()

    if rows:
        out = []
        for row in reversed(rows):
            xtime, xnick, xmsg = row
            out.append(u"{} <{}> {}".format(xtime[:-7], xnick, xmsg))
        say("The last {} lines of conversation: {}".format(num,
            web.haste(u'\n'.join(out).encode('utf-8'), 'txt')))
    else:
        say("*Silence*")


@hook.command('l')
@hook.command
def last(inp, nick='', chan='', input=None, db=None, say=None):
    """last <phrase> - Finds the last occurence of a phrase."""
    row = db.execute('select time, nick, msg, uts from logfts where logfts match ? and uts < ? order by uts desc limit 1',
        ('msg:"{}"* AND chan:{}'.format(inp, chan.strip('#')), (time.time() - 1))).fetchone()

    if row:
        xtime, xnick, xmsg, xuts = row
        say("%s last said \"%s\" on %s (%s ago)" %
            (xnick, xmsg, xtime[:-7], timesince.timesince(xuts)))
    else:
        say("Never!")


@hook.command
def first(inp, chan='', input=None, db=None, say=None):
    """first <phrase> - Finds the first occurence of a phrase."""
    row = db.execute('select time, nick, msg, uts from logfts where logfts match ? order by uts asc limit 1',
        ('msg:"{}"* AND chan:{}'.format(inp, chan.strip('#')), )).fetchone()

    if row:
        xtime, xnick, xmsg, xuts = row
        say("%s first said \"%s\" on %s (%s ago)" %
            (xnick, xmsg, xtime[:-7], timesince.timesince(xuts)))
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

