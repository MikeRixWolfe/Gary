import time
import re
from datetime import datetime
from util import hook

timestamp_format = '%H:%M:%S'

formats = {
    'PRIVMSG': '<%(nick)s> %(msg)s',
    'PART': '-!- %(nick)s [%(user)s@%(host)s] has left %(chan)s [%(msg)s]',
    'JOIN': '-!- %(nick)s [%(user)s@%(host)s] has joined %(param0)s',
    'MODE': '-!- mode/%(chan)s [%(param_tail)s] by %(nick)s',
    'KICK': '-!- %(param1)s was kicked from %(chan)s by %(nick)s [%(msg)s]',
    'TOPIC': '-!- %(nick)s changed the topic of %(chan)s to: %(msg)s',
    'QUIT': '-!- %(nick)s has quit IRC [%(msg)s]',
    'NICK': '-!- %(nick)s [%(user)s@%(host)s] is now known as %(msg)s',
    'PING': '',
    'NOTICE': ''
}

ctcp_formats = {
    'ACTION': '* %(nick)s %(ctcpmsg)s',
    'VERSION': '',
    'PING': '',
    'TIME': '',
    'FINGER': ''
}

irc_color_re = re.compile(r'(\x03(\d{1,2}(,\d{1,2})?)|[\x0f\x02\x16\x1f])')



def db_init(db):
    db.execute("create table if not exists log(time, server, chan, nick, user,"
               " action, msg, uts, primary key(time, server, chan, nick))")
    db.execute("create table if not exists seen(time, server, chan, nick, user,"
               " action, msg, uts, primary key(server, chan, nick))")
    db.execute("create table if not exists links(time, server, chan, nick, user,"
               " action, msg, uts, primary key(time, server, chan, nick))")
    db.execute("create index if not exists uts_idx on log(uts)")
    db.execute("create index if not exists msg_idx on log(msg)")
    db.execute("create index if not exists chan_idx on log(chan)")
    db.execute("create index if not exists nick_idx on log(nick)")
    db.commit()


def log_chat(db, server, chan, nick, user, host, action, msg):
    mask = user.lower() + "@" + host.lower()
    db.execute("insert into log(time, server, chan, nick, user, action, msg, uts)"
               " values(?, lower(?), lower(?), lower(?), lower(?), upper(?), ?, ?)",
               (datetime.now(), server, chan, nick, mask, action, msg, time.time()))
    db.commit()


def log_seen(db, server, chan, nick, user, host, action, msg):
    mask = user.lower() + "@" + host.lower()
    db.execute("insert or replace into seen(time, server, chan, nick, user, action, msg, uts)"
               " values(?, lower(?), lower(?), lower(?), lower(?), upper(?), ?, ?)",
               (datetime.now(), server, chan, nick, mask, action, msg, time.time()))
    db.commit()


def log_link(db, server, chan, nick, user, host, action, msg):
    mask = user.lower() + "@" + host.lower()
    db.execute("insert into links(time, server, chan, nick, user, action, msg, uts)"
               " values(?, lower(?), lower(?), lower(?), lower(?), upper(?), ?, ?)",
               (datetime.now(), server, chan, nick, mask, action, msg, time.time()))
    db.commit()


def localtime(format):
    return time.strftime(format, time.localtime())


def format_output(input):
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
        ctcp[1] = irc_color_re.sub('', ctcp[1])
        args['ctcpcmd'], args['ctcpmsg'] = ctcp
        format = ctcp_formats.get(args['ctcpcmd'], '')

    return format % args


@hook.singlethread
@hook.event('*')
def log(paraml, input=None, bot=None, db=None):
    timestamp = localtime(timestamp_format)

    if input.command == 'QUIT':  # these are temporary fixes until proper
        input.chan = 'quit'      # presence tracking is implemented
    if input.command == 'NICK':  # fix me please
        input.chan = 'nick'

    out = format_output(input)
    if not out:  # don't log this
        return

    if input.chan and input.nick and input.user \
        and input.command in formats.keys() \
        and input.nick != input.conn.nick:
        db_init(db)

        # format data
        input.msg = irc_color_re.sub('', input.msg)
        if input.command == 'PRIVMSG' and input.msg.count('\x01') >= 2:
            input.msg = irc_color_re.sub('',
                input.msg.split('\x01', 2)[1].split(' ', 1)[1])
            input.msg = "* {} {}".format(input.nick, input.msg)
        if input.command == 'KICK':
            input.msg = "{} [{}]".format(paraml[1], input.msg)
        if input.command == 'MODE':
            input.msg = ' '.join(paraml[1:])
        if input.command == 'JOIN':
            input.msg = ''

        log_chat(db, input.server, input.chan, input.nick,
            input.user, input.host, input.command, input.msg)
        if input.command not in ('MODE'):
            log_seen(db, input.server, input.chan, input.nick,
                input.user, input.host, input.command, input.msg)
        if re.match('https?://(?:www\.)?([^/]+)/?\S*', input.msg):
            log_link(db, input.server, input.chan, input.nick,
                input.user, input.host, input.command, input.msg)

        print timestamp, input.chan, out.encode('ascii', 'ignore')
