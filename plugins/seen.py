import re
from time import time
from datetime import datetime
from util import hook, timesince, text

formats = {
    'PRIVMSG': 'in %(chan)s saying "%(msg)s"',
    'PART': 'leaving %(chan)s with reason: %(msg)s',
    'JOIN': 'joining %(chan)s',
    'KICK': 'kicking %(who)s from %(chan)s with reason: %(msg)s',
    'KICKEE': 'being kicked from %(chan)s by %(nick)s with reason: %(msg)s',
    'TOPIC': 'in %(chan)s changing the topic to: %(msg)s',
    'QUIT': 'quitting IRC with reason: %(msg)s',
    'NICK': 'in %(chan)s changing nick to %(msg)s'
}


@hook.command(autohelp=False)
def around(inp, nick='', chan='', say='', db=None, input=None):
    ".around [minutes] - Lists what nicks have been active in the last [minutes] minutes, defaults to 15"
    minutes = 15
    length = 430

    if inp.isdigit():
        minutes = int(inp)

    period = time() - (minutes * 60)
    out = "Users around in the last {} minutes: ".format(minutes)

    if inp == 'today':
        today = datetime.today()
        period = float(datetime(today.year, today.month, today.day).strftime('%s'))
        out = "Users around today: "

    rows = db.execute("select distinct nick from seen where uts >= ? and "
        "server = lower(?) and chan = lower(?) order by nick", (period,
        input.server, chan)).fetchall()
    rows = ([row[0] for row in rows] if rows else None)

    if rows:
        out += ', '.join(rows)
        if len(out) >= length:
            truncstr = prefix[:length].rsplit(' ', 1)[0]
            out = truncstr + " and {} others".format(len(out[len(truncstr):].split()))
        say(out)
    else:
        say("No one!")


@hook.command
def seen(inp, say='', nick='', db=None, input=None):
    ".seen <nick> - Tell when a nickname was last in active in irc"
    if input.conn.nick.lower() == inp.lower():
        return "You need to get your eyes checked."
    if inp.lower() == nick.lower():
        return "Have you looked in a mirror lately?"

    rows = db.execute("select chan, nick, action, msg, uts from seen where server = lower(?) and chan in (lower(?), 'quit', 'nick') and (nick = lower(?) or (action = 'KICK' and msg = ?)) order by uts desc limit 1",
        (input.server, input.chan, inp, inp.lower() + "%")).fetchone()

    if rows:
        row = dict(zip(['chan', 'nick', 'action', 'msg', 'uts'], rows))
        reltime = timesince.timesince(row['uts'])
        if row['action'] == 'KICK':
            row['who'] = row['msg'].split(' ')[:1][0]
            row['msg'] = ' '.join(row['msg'].split(' ')[1:]).strip('[]')
            if inp.lower() != row['who'].lower():
                row['action'] = 'KICKEE'

        format = formats.get(row['action'])

        out = '{} was last seen {} ago '.format(inp, reltime)
        say(out + format % row)
    else:
        return "I've never seen %s" % inp
