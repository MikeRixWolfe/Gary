import re
from util import hook


def is_admin(bot, input):
    nick = input.nick.lower()
    admins = bot.config.get('admins', [])
    if nick in admins and input.conn.users.get(nick, False):
        return True
    else:
        return False

@hook.sieve
def sieve_suite(bot, input, func, kind, args):
    moded = bot.config.get('moded', [])
    allowed = bot.config.get('allowed', [])
    disabled = bot.config.get('disabled', [])
    ignored = bot.config.get('ignored', [])
    muted = bot.config.get('muted', [])
    restricted = bot.config.get('restricted', [])
    acl = bot.config.get('acls', {})

    # log everything
    #if func.__name__.lower() == "log":
    #    return input

    # disable function
    if kind in ("event", "regex"):
        if func.__name__.lower() in disabled:
            return None

    if kind in ("command"):
        if func.__name__.lower() in disabled and not is_admin(bot, input):
            return None


    # disable plugin
    fn = re.match(r'^plugins/(.+\.py$)', func._filename)
    if fn and fn.group(1).lower() in disabled:
        return None

    # acls
    if acl:
        if 'deny-except' in acl:
            allowed_channels = map(unicode.lower, acl['deny-except'])
            if input.chan.lower() not in allowed_channels:
                return None
        if 'allow-except' in acl:
            denied_channels = map(unicode.lower, acl['allow-except'])
            if input.chan.lower() in denied_channels:
                return None

    # admins
    if args.get('adminonly'):
        if not is_admin(bot, input):
            return None

    # mods
    if args.get('modonly'):
        if input.nick.lower() not in moded or not is_admin(bot, input):
            return None

    # restricted
    if input.chan in restricted:
        allowlist = moded + allowed
        if input.nick.lower() not in allowlist and not is_admin(bot, input):
            return None

    # ignores
    if any(x in ignored for x in map(lambda y:y.lower(),
            [input.host, input.user, input.nick, input.chan])):
        if not is_admin(bot, input):
            return None

    # mutes
    if input.chan in muted:
        if not is_admin(bot, input):
            return None

    return input
