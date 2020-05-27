import re
from time import time
from datetime import datetime
from util import hook, timesince, text

formats = {
    'PRIVMSG': 'saying "%(msg)s"',
    'ACTION': 'saying "%(msg)s"',
    'PART': 'leaving %(chan)s with reason "%(msg)s"',
    'JOIN': 'joining %(chan)s',
    'KICK': 'kicking %(who)s from %(chan)s with reason %(msg)s',
    'KICKEE': 'being kicked from %(chan)s by %(nick)s with reason %(msg)s',
    'TOPIC': 'changing %(chan)s\'s topic to "%(msg)s"',
    'QUIT': 'quitting IRC with reason "%(msg)s"',
    'NICK': 'changing nick to %(msg)s'
}


@hook.regex(r'^seen (\S+)')
@hook.command
def seen(inp, say='', nick='', db=None, input=None):
    """seen <nick> - Tell when a nickname was last in active in IRC."""
    try:
        inp = inp.split(' ')[0]
    except:
        inp = inp.group(1)

    if input.conn.nick.lower() == inp.lower():
        return "You need to get your eyes checked."
    if inp.lower() == nick.lower():
        return "Have you looked in a mirror lately?"

    rows = db.execute("select chan, nick, action, msg, uts from logfts where logfts match ? order by cast(uts as decimal) desc limit 1",
        ('((chan:"{}" OR chan:"nick" OR chan:"quit") AND nick:"{}") OR (chan:"{}" AND action:"kick" AND msg:"{}")'.format(input.chan.strip('#'), inp, input.chan.strip('#'), inp),)).fetchone()

    if rows:
        row = dict(zip(['chan', 'nick', 'action', 'msg', 'uts'], rows))
        reltime = timesince.timesince(float(row['uts']))
        if row['action'] == 'KICK':
            row['who'], row['msg'] = row['msg'].split(' ', 1)
            if inp.lower() != row['nick'].lower():
                row['action'] = 'KICKEE'

        format = formats.get(row['action'])

        out = '{} was last seen {} ago '.format(inp, reltime)
        say(out + format % row)
    else:
        return "I've never seen %s" % inp

