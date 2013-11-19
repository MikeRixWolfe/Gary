"""
ignore.py: written by MikeFightsBears 2013
"""

import json
from util import hook


@hook.sieve
def ignore_sieve(bot, input, func, type, args):
    """ blocks input from ignored channels/hosts """
    ignorelist = bot.config["ignored"]
    # don't block input to event hooks
    if type == "event":
        return input

    if ignorelist:
        if input.nick.lower() in ignorelist or input.user.strip('~').lower() in ignorelist or input.user.lower() in ignorelist or input.chan in ignorelist or input.host in ignorelist:
            return None
    return input


@hook.command(autohelp=False)
def ignored(inp, notice=None, bot=None, say=None):
    """.ignored - Lists ignored channels/users."""
    ignorelist = bot.config["ignored"]
    if ignorelist:
        return "Ignored channels/users are: %s" % format(", ".join(ignorelist))
    else:
        return "No masks are currently ignored."
    return


@hook.command(adminonly=True)
def ignore(inp, say=None, notice=None, bot=None, config=None):
    """.ignore <channel|nick|host> - Makes the bot ignore <channel|user|host>."""
    target = inp.lower()
    ignorelist = bot.config["ignored"]
    if target in ignorelist:
        return "%s is already ignored." % format(target)
    else:
        admins = bot.config.get('admins', [])
        if target in admins:
            return "I can not ignore a bot admin"
        else: 
            ignorelist.append(target)
            ignorelist.sort()
            json.dump(bot.config, open('config', 'w'), sort_keys=True, indent=2)
            return "%s has been ignored." % format(target)
    return


@hook.command(adminonly=True)
def unignore(inp, say=None, notice=None, bot=None, config=None):
    """.unignore <channel|user> - Makes the bot listen to <channel|user>."""
    target = inp.lower()
    ignorelist = bot.config["ignored"]
    if target in ignorelist:
        ignorelist.remove(target)
        ignorelist.sort()
        json.dump(bot.config, open('config', 'w'), sort_keys=True, indent=2)
        return "%s has been unignored." % format(target)
    else:
        return "%s is not ignored." % format(target)
    return
