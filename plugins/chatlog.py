import datetime
import time
from util import hook, text, timesince, tokenize, web


@hook.command('l')
@hook.command
def last(inp, nick='', chan='', input=None, db=None, say=None):
    """l[ast] <phrase> - Finds the last occurence of a phrase. Flag -G to search all channels."""
    try:
        inp = [t.lower() for t in inp.split(' ') if t]
        inp.remove('-g')
        g = True
        inp = ' '.join(inp)
    except:
        g = False
        inp = ' '.join(inp)

	if not inp:
		return "Check your input and try again."

    if g:
		row = db.execute('select time, chan, nick, msg, uts from logfts where logfts match ? and cast(uts as decimal) < ? order by cast(uts as decimal) desc limit 1',
			(tokenize.build_query(inp), (time.time() - 1))).fetchone()
    else:
		row = db.execute('select time, chan, nick, msg, uts from logfts where logfts match ? and cast(uts as decimal) < ? order by cast(uts as decimal) desc limit 1',
			('{} AND chan:"{}"'.format(tokenize.build_query(inp), chan.strip('#')), (time.time() - 1))).fetchone()

    if row:
        xtime, xchan, xnick, xmsg, xuts = row
        say("%s last said \"%s\" in %s on %s (%s ago)" %
            (xnick, xmsg, xchan, xtime.split(' ')[0], timesince.timesince(float(xuts))))
    else:
        say("Never!")


@hook.command('f')
@hook.command
def first(inp, chan='', input=None, db=None, say=None):
    """f[irst] [-G] <phrase> - Finds the first occurence of a phrase. Flag -G to search all channels."""
    try:
        inp = [t.lower() for t in inp.split(' ') if t]
        inp.remove('-g')
        g = True
        inp = ' '.join(inp)
    except:
        g = False
        inp = ' '.join(inp)

    if not inp:
        return "Check your input and try again."

    if g:
        row = db.execute('select time, chan, nick, msg, uts from logfts where logfts match ? order by cast(uts as decimal) asc limit 1',
            (tokenize.build_query(inp), )).fetchone()
    else:
        row = db.execute('select time, chan, nick, msg, uts from logfts where logfts match ? order by cast(uts as decimal) asc limit 1',
            ('{} AND chan:"{}"'.format(tokenize.build_query(inp), chan.strip('#')), )).fetchone()

    if row:
        xtime, xchan, xnick, xmsg, xuts = row
        say("%s first said \"%s\" in %s on %s (%s ago)" %
            (xnick, xmsg, xchan, xtime.split(' ')[0], timesince.timesince(float(xuts))))
    else:
        say("Never!")


@hook.command
def said(inp, chan='', input=None, db=None, say=None):
    """said <phrase> - Finds users who has said a phrase. Flag -G to search all channels."""
    try:
        inp = [t.lower() for t in inp.split(' ') if t]
        inp.remove('-g')
        g = True
        inp = ' '.join(inp)
    except:
        g = False
        inp = ' '.join(inp)

    if not inp:
        return "Check your input and try again."

    if g:
        rows = db.execute('select distinct nick from logfts where logfts match ? order by nick',
            (tokenize.build_query(inp), )).fetchall()
        rows = ([row[0] for row in rows] if rows else None)
    else:
        rows = db.execute('select distinct nick from logfts where logfts match ? order by nick',
            ('{} AND chan:"{}"'.format(tokenize.build_query(inp), chan.strip('#')), )).fetchall()
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
    """rotw [-G] <phrase> - Displays the royalty of the word. Flag -G to search all channels."""
    try:
        inp = [t.lower() for t in inp.split(' ') if t]
        inp.remove('-g')
        g = True
        inp = ' '.join(inp)
    except:
        g = False
        inp = ' '.join(inp)

    if not inp:
        return "Check your input and try again."

    if g:
        total = db.execute('select count(1) from logfts where logfts match ?',
            (tokenize.build_query(inp), )).fetchone()
        total = total[0] if total else None

        rows = db.execute('select distinct lower(nick), count(1) from logfts where logfts match ? group by lower(nick) order by count(1) desc limit 10',
            (tokenize.build_query(inp), )).fetchall()
    else:
        total = db.execute('select count(1) from logfts where logfts match ?',
            ('{} AND chan:{}'.format(tokenize.build_query(inp), chan.strip('#')), )).fetchone()
        total = total[0] if total else None

        rows = db.execute('select distinct lower(nick), count(1) from logfts where logfts match ? group by lower(nick) order by count(1) desc limit 10',
            ('{} AND chan:{}'.format(tokenize.build_query(inp), chan.strip('#')), )).fetchall()

    if rows and total:
        out = []
        suffixes = {1: 'st', 2: 'nd', 3: 'rd'}
        for i, row in enumerate(rows):
            out.append('{}{}: {} {:,d} uses ({:.2%})'.format(i + 1,
                suffixes.get(i + 1, 'th'), row[0], row[1], float(row[1])/total))
        if g:
            say('There are {:,d} uses of "{}". {}'.format(total, inp, ', '.join(out)))
        else:
            say('There are {:,d} uses of "{}" in {}. {}'.format(total, inp, chan, ', '.join(out)))
    else:
        say("No one!")

