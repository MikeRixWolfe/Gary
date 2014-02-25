import re
from util import hook


@hook.sieve
def sieve_suite(bot, input, func, kind, args):
    admins = bot.config.get('admins', [])
    opers = bot.config.get('opers', [])
    voices = bot.config['voice']
    disabled = bot.config.get('disabled', [])
    ignored = bot.config.get('ignored', [])
    muted = bot.config.get('muted', [])
    restricted = bot.config.get('restrictedmode', [])
    acl = bot.config.get('acls', {})

    if kind == "event":
        if func.__name__.lower() in disabled:
            return None

    if kind == "command":
        if input.trigger.lower() in disabled and input.nick.lower() not in admins:
            return None

    if kind == "regex":
        if func.__name__.lower() in disabled and input.nick.lower() not in admins:
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
        if input.nick.lower() not in admins:
            return None

    if args.get('operonly'):
        if input.nick.lower() not in admins+opers:
            return None

    if input.chan in restricted:
        allowlist = admins + opers + voicers
        if input.nick.lower() not in allowlist:
            return None

    # Possibly move into command/regex above
    if input.host.lower() in ignored or input.user.lower() in ignored or \
            input.nick.lower() in ignored or input.chan.lower() in ignored:
        if input.nick.lower() not in admins:
            return None

    if input.chan in muted:
        if input.nick.lower() not in admins:
            return None

    return input
