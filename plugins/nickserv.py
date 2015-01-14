"""
These functions are entirely for tracking NickServ status of users. NickServ
status of users is used for admin functions which require the user to be
identified for security reasons. This may be useful if the adminonly concept
is expanded to a full permissions manager for security on priveleged groups.
"""

from util import hook, text


@hook.command(autohelp=False)
def ident(inp, nick='', conn=None):
    """.ident - Tries to update your NickServ ident status."""
    if not conn.users.get(conn.nick.lower(), False):
        return("I cannot identify with NickServ; priviledged functions disabled.")
    else:
        conn.msg(conn.conf.get('nickserv_name', 'nickserv'),
            conn.conf.get('nickserv_ident_command', 'INFO %s') % nick.lower())
        return "NickServ ident status updated."


@hook.command(autohelp=False)
def status(inp, nick=None, say=None, conn=None):
    """.status [all|green|red] - Gets your perceived NickServ status or a specified group."""
    if inp == 'all':
        users = conn.users
    elif inp == 'green':
        users = {k:v for k,v in conn.users.items() if v}
    elif inp == 'red':
        users = {k:v for k,v in conn.users.items() if not v}
    else:
        return "You look %s to me" % ("\x033identified\x0f" if conn.users.get(nick, None)
            else "\x034unidentified\x0f")

    outs = text.chunk_str(', '.join(sorted(["\x033%s\x0f" % k if v else "\x034%s\x0f" % k
        for k, v in users.items()], key=lambda x: x)))

    for out in outs: say(out)


@hook.event('*')
def nickserv_tracking(paraml, nick=None, input=None, conn=None):
    if input.command in ('QUIT', 'NICK', 'JOIN', 'PART', 'PRIVMSG', 'KICK') and \
            conn.users.get(conn.nick.lower(), False):
        nick = nick.lower()
        nickserv_name = conn.conf.get('nickserv_name', 'nickserv')
        nickserv_ident = conn.conf.get('nickserv_ident_command', 'INFO %s')
        if input.command == 'JOIN':
            if not conn.users.get(nick, False):
                conn.msg(nickserv_name, nickserv_ident % nick)
        if input.command == 'PRIVMSG':
            if nick not in conn.users.keys():
                 conn.msg(nickserv_name, nickserv_ident % nick)
        elif input.command in ('QUIT', 'PART', 'NICK', 'KICK'):
            if input.command == 'KICK':
                nick = paraml[1]
            conn.users.pop(nick, None)
            if input.command == 'NICK':
                conn.msg(nickserv_name, nickserv_ident % paraml[0])


@hook.event('NOTICE')
def noticed(paraml, chan='', conn=None):
    if paraml[0] == conn.nick and \
            chan.lower() == conn.conf.get('nickserv_name', 'nickserv'):
        if "Nickname:" in paraml[1]:
            if "ONLINE" in paraml[1]:
                conn.users[str(paraml[1].split()[1]).lower()] = True
            else:
                conn.users[str(paraml[1].split()[1]).lower()] = False
        elif "not registered" in paraml[1] or "is private" in paraml[1]:
            conn.users[str(paraml[1].split()[2]).lower()[2:-2]] = False

