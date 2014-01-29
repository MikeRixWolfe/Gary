"""
log.py: written by MikeFightsBears 2014
"""

import time
import re
from datetime import datetime

from util import hook

timestamp_format = '%H:%M:%S'

formats = {'PRIVMSG': '<%(nick)s> %(msg)s',
    'PART': '-!- %(nick)s [%(user)s@%(host)s] has left %(chan)s',
    'JOIN': '-!- %(nick)s [%(user)s@%(host)s] has joined %(param0)s',
    'MODE': '-!- mode/%(chan)s [%(param_tail)s] by %(nick)s',
    'KICK': '-!- %(param1)s was kicked from %(chan)s by %(nick)s [%(msg)s]',
    'TOPIC': '-!- %(nick)s changed the topic of %(chan)s to: %(msg)s',
    'QUIT': '-!- %(nick)s has quit [%(msg)s]',
    'NICK': '',
    'PING': '',
    'NOTICE': ''
}

ctcp_formats = {'ACTION': '* %(nick)s %(ctcpmsg)s'}

irc_color_re = re.compile(r'(\x03(\d+,\d+|\d)|[\x0f\x02\x16\x1f])')

def db_init(db):
    db.execute("create table if not exists log(time, server, chan, nick, user,"
               " action, msg, uts, primary key(time, server, chan, nick))")
    db.commit()


def localtime(format):
    return time.strftime(format, time.localtime())

    
def beautify(input):
    format = formats.get(input.command, '%(raw)s')
    args = dict(input)

    leng = len(args['paraml'])
    for n, p in enumerate(args['paraml']):
        args['param' + str(n)] = p
        args['param_' + str(abs(n - leng))] = p

    args['param_tail'] = ' '.join(args['paraml'][1:])
    args['msg'] = irc_color_re.sub('', args['msg'])

    if input.command == 'PRIVMSG' and input.msg.count('\x01') >= 2:
        ctcp = input.msg.split('\x01', 2)[1].split(' ', 1)
        if len(ctcp) == 1:
            ctcp += ['']
        args['ctcpcmd'], args['ctcpmsg'] = ctcp
        format = ctcp_formats.get(args['ctcpcmd'],
                '%(nick)s [%(user)s@%(host)s] requested unknown CTCP '
                '%(ctcpcmd)s from %(chan)s: %(ctcpmsg)s')

    return format % args


@hook.singlethread
@hook.event('*')
def logtest(paraml, input=None, bot=None, db=None):
    timestamp = localtime(timestamp_format)
    beau = beautify(input)

    if beau == '':  # don't log this
        return

    if input.chan and input.nick != input.conn.nick and input.command in formats.keys() and (input.chan[0] == '#' or input.chan == input.nick):
        db_init(db)
        log_chat(db, input.server, input.chan, input.nick, input.user, input.host,
                 input.command, re.sub(r'^<' + input.nick + '>\ ','', beau.encode('ascii', 'ignore'), 1))

    print timestamp, input.chan, beau.encode('ascii', 'ignore')


def log_chat(db, server, chan, nick, user, host, action, msg):
    db.execute("insert into log(time, server, chan, nick, user, action, msg, uts)"
               " values(?, lower(?), lower(?), lower(?), lower(?), upper(?), ?, ?)", 
               (datetime.now(), server, chan, nick, user + "@" + host, action, msg, time.time()))
    db.commit()

