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
    opers = bot.config.get('opered', [])
    voices = bot.config.get('voiced', [])
    disabled = bot.config.get('disabled', [])
    ignored = bot.config.get('ignored', [])
    muted = bot.config.get('muted', [])
    restricted = bot.config.get('restricted', [])
    acl = bot.config.get('acls', {})

    if kind == "event":
        if func.__name__.lower() in disabled:
            return None

    if kind == "command":
        if func.__name__.lower() in disabled and not is_admin(bot, input):
            return None

    if kind == "regex":
        if func.__name__.lower() in disabled:
            return None

    fn = re.match(r'^plugins/(.+\.py$)', func._filename)
    if fn and fn.group(1).lower() in disabled:
        return None

    if acl:
        if 'deny-except' in acl:
            allowed_channels = map(unicode.lower, acl['deny-except'])
            if input.chan.lower() not in allowed_channels:
                return None
        if 'allow-except' in acl:
            denied_channels = map(unicode.lower, acl['allow-except'])
            if input.chan.lower() in denied_channels:
                return None

    if args.get('adminonly'):
        if not is_admin(bot, input):
            return None

    if args.get('operonly'):
        if input.nick.lower() not in opers or not is_admin(bot, input):
            return None

    if input.chan in restricted:
        allowlist = opers + voices
        if input.nick.lower() not in allowlist or not is_admin(bot, input):
            return None

    # Possibly move into command/regex above
    if input.host.lower() in ignored or input.user.lower() in ignored or \
            input.nick.lower() in ignored or input.chan.lower() in ignored:
        if not is_admin(bot, input):
            return None

    if input.chan in muted:
        if not is_admin(bot, input):
            return None

    return input
