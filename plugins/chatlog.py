import re
from time import time
from sqlite3 import OperationalError
from util import hook, text, timesince, tokenize, web


formats = {
    'PRIVMSG': '{nick} {context} on {date} ({timesince} ago) in {chan} with message "{msg}" {log_url}',
    'ACTION': '{nick} {context} on {date} ({timesince} ago) in {chan} with message "{msg}" {log_url}',
    'PART': '{nick} {context} on {date} ({timesince} ago) leaving {chan} with reason "{msg}" {log_url}',
    'JOIN': '{nick} {context} on {date} ({timesince} ago) joining {chan} {log_url}',
    'KICK': '{nick} {context} on {date} ({timesince} ago) kicking {who} from {chan} with reason {msg} {log_url}',
    'KICKEE': '{who} {context} on {date} ({timesince} ago) being kicked from {chan} by {nick} with reason {msg} {log_url}',
    'TOPIC': '{nick} {context} on {date} ({timesince} ago) changing {chan}\'s topic to "{msg}" {log_url}',
    'QUIT': '{nick} {context} on {date} ({timesince} ago) quitting IRC with reason "{msg}" {log_url}',
    'NICK': '{nick} {context} on {date} ({timesince} ago) changing nick to {msg} {log_url}',
    'NICKEE': '{msg} {context} on {date} ({timesince} ago) changing nick from {nick} {log_url}'
}


def is_global(inp):
    _inp = ' '.join([t for t in inp.split(' ') if t.lower() != '-g'])
    if inp == _inp:
        return inp, False
    else:
        return _inp, True


@hook.command('l')
@hook.command
def last(inp, nick='', chan='', bot=None, db=None, say=None):
    """l[ast] [-G] <phrase> - Finds the last occurence of a phrase. Flag -G to search all channels."""
    inp, _global = is_global(inp)

    if not inp:
        return "Check your input and try again."

    if _global:
        match_clause = tokenize.build_query(inp)
    else:
        match_clause = '{} AND chan:"{}"'.format(tokenize.build_query(inp), chan.strip('#'))

    try:
        row = db.execute("select uts, time, chan, nick, action, msg from logfts where logfts match ? and (msg not like '!%' and msg not like ';%' and msg not like '.%') and cast(uts as decimal) < ? and action = 'PRIVMSG' order by cast(uts as decimal) desc limit 1",
            (match_clause, (time() - 1))).fetchone()
    except OperationalError:
        return "Error: must contain one inclusive match clause (+/=)."

    if row:
        row = dict(zip(['uts', 'time', 'chan', 'nick', 'action', 'msg'], row))

        row['date'] = row['time'].split(' ')[0]
        row['timesince'] = timesince.timesince(float(row['uts']))
        if bot.config.get("logviewer_url"):
            row['log_url'] = web.try_googl(bot.config["logviewer_url"].format(row['chan'].strip('#'), *row['time'].split()))
        else:
            row['log_url'] = ''

        say(formats[row['action']].format(context='last said that', **row).strip())
    else:
        say("Never!")


@hook.command('f')
@hook.command
def first(inp, chan='', bot=None, db=None, say=None):
    """f[irst] [-G] <phrase> - Finds the first occurence of a phrase. Flag -G to search all channels."""
    inp, _global = is_global(inp)

    if not inp:
        return "Check your input and try again."

    if _global:
        match_clause = tokenize.build_query(inp)
    else:
        match_clause = '{} AND chan:"{}"'.format(tokenize.build_query(inp), chan.strip('#'))

    try:
        row = db.execute("select uts, time, chan, nick, action, msg from logfts where logfts match ? and (msg not like '!%' and msg not like ';%' and msg not like '.%') and action = 'PRIVMSG' limit 1",
            (match_clause, )).fetchone()
    except OperationalError:
        return "Error: must contain one inclusive match clause (+/=)."

    if row:
        row = dict(zip(['uts', 'time', 'chan', 'nick', 'action', 'msg'], row))

        row['date'] = row['time'].split(' ')[0]
        row['timesince'] = timesince.timesince(float(row['uts']))
        if bot.config.get("logviewer_url"):
            row['log_url'] = web.try_googl(bot.config["logviewer_url"].format(row['chan'].strip('#'), *row['time'].split()))
        else:
            row['log_url'] = ''

        say(formats[row['action']].format(context='first said that', **row).strip())
    else:
        say("Never!")


@hook.regex(r'^seen ((?:-[gG] )?(?:\S+))')
@hook.command
def seen(inp, chan='', nick='', bot=None, db=None, say=None, input=None):
    """seen [-G] <nick> - Tell when a nickname was last in active in IRC. Flag -G to search all channels."""
    try:
        inp = inp.group(1)
    except:
        pass

    inp, _global = is_global(inp)

    if input.conn.nick.lower() == inp.lower():
        return "You need to get your eyes checked."
    if inp.lower() == nick.lower():
        return "Have you looked in a mirror lately?"

    if _global:
        row = db.execute("select uts, time, chan, nick, action, msg from logfts where logfts match ? order by cast(uts as decimal) desc limit 1",
            ('nick:^"{}" OR (action:"kick" AND msg:^"{}") OR (chan:"nick" AND msg:^"{}")'.format(inp, inp, inp),)).fetchone()
    else:
        row = db.execute("select uts, time, chan, nick, action, msg from logfts where logfts match ? order by cast(uts as decimal) desc limit 1",
            ('((chan:"{}" OR chan:"nick" OR chan:"quit") AND nick:^"{}") OR (chan:"{}" AND action:"kick" AND msg:^"{}") OR (chan:"nick" AND msg:^"{}")'.format(chan.strip('#'), inp, chan.strip('#'), inp, inp),)).fetchone()

    if row:
        row = dict(zip(['uts', 'time', 'chan', 'nick', 'action', 'msg'], row))

        row['date'] = row['time'].split(' ')[0]
        row['timesince'] = timesince.timesince(float(row['uts']))
        if bot.config.get("logviewer_url"):
            row['log_url'] = web.try_googl(bot.config["logviewer_url"].format(row['chan'].strip('#'), *row['time'].split()))
        else:
            row['log_url'] = ''

        if row['action'] == 'KICK':
            row['who'], row['msg'] = row['msg'].split(' ', 1)
            if inp.lower() != row['nick'].lower():
                row['action'] = 'KICKEE'

        if row['action'] == 'NICK':
            if inp.lower() != row['nick'].lower():
                row['action'] = 'NICKEE'

        say(formats[row['action']].format(context='was last seen', **row).strip())
    else:
        return "I've never seen {}".format(inp)


@hook.command
def rotw(inp, chan='', db=None, say=None):
    """rotw [-G] <phrase> - Displays the royalty of the word. Flag -G to search all channels."""
    inp, _global = is_global(inp)

    if not inp:
        return "Check your input and try again."

    if _global:
        match_clause = tokenize.build_query(inp)
    else:
        match_clause = '{} AND chan:"{}"'.format(tokenize.build_query(inp), chan.strip('#'))

    try:
        total = db.execute('select count(1) from logfts where logfts match ?',
            (match_clause, )).fetchone()
        total = total[0] if total else None

        rows = db.execute("select distinct lower(nick), count(1) from logfts where logfts match ? group by lower(nick) order by count(1) desc limit 10",
            (match_clause, )).fetchall()
    except OperationalError:
        return "Error: must contain one inclusive match clause (+/=)."

    if rows and total:
        out = []
        suffixes = {1: 'st', 2: 'nd', 3: 'rd'}
        for i, row in enumerate(rows):
            out.append('{}{}: {} {:,d} uses ({:.2%})'.format(i + 1,
                suffixes.get(i + 1, 'th'), row[0], row[1], float(row[1])/total))
        if _global:
            say('There are {:,d} uses of "{}". {}'.format(total, inp, ', '.join(out)))
        else:
            say('There are {:,d} uses of "{}" in {}. {}'.format(total, inp, chan, ', '.join(out)))
    else:
        say("No one!")

