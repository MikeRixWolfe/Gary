import re
from util import hook


@hook.sieve
def sieve_suite(bot, input, func, kind, args):
    if kind == "event"
        return input

    if kind == "command":
        if input.trigger in bot.config.get('disabled', []):
            return None

    fn = re.match(r'^plugins/(.+\.py$)', func._filename)
    disabled = bot.config.get('disabled', [])
    if fn and fn.group(1).lower() in disabled:
        return None

    acl = bot.config.get('acls', {}).get(func.__name__)
    if acl:
        if 'deny-except' in acl:
            allowed_channels = map(unicode.lower, acl['deny-except'])
            if input.chan.lower() not in allowed_channels:
                return None
        if 'allow-except' in acl:
            denied_channels = map(unicode.lower, acl['allow-except'])
            if input.chan.lower() in denied_channels:
                return None

    if args.get('adminonly') == True:
        admins = bot.config.get('admins', [])
        if input.nick.strip(' ~@%+') not in admins:# or input.chan[0] != "#":
            return None

    if args.get('operonly') == True:
        admins = bot.config.get('admins', [])
        opers = bot.config.get('opers', [])
        if input.nick.strip(' ~@%+') not in admins and input.nick.strip(' ~@%+') not in opers:# or input.chan[0] != "#":
            return None

    ignored = bot.config.get('ignored', [])
    if input.host in ignored or input.nick in ignored or input.nick.lower() in ignored or input.chan in ignored:
        if input.user.strip(' ~') not in admins and input.nick not in admins:
            return None

    if input.chan in mutelist:
        admins = bot.config.get('admins', [])
        if input.user.strip(' ~') not in admins and input.nick not in admins:
            return None

    return input
