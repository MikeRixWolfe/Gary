"""
mute.py: written by MikeFightsBears.com
"""

import json
from util import hook


@hook.sieve
def mute_sieve(bot, input, func, type, args):
    """ blocks input from muted channels/hosts """
    mutelist = bot.config["muted"]
    # don't block input to event hooks
    if type == "event":
        return input
    if input.chan in mutelist:
        admins = bot.config.get('admins', [])
        if input.user.strip(' ~') not in admins and input.nick not in admins:
            return None

    return input


@hook.command(adminonly=True, autohelp=False)
def mute(inp, input=None, say=None, notice=None, bot=None, config=None):
    """.mute - Makes the bot mute channel."""
    target = input.chan
    mutelist = bot.config["muted"]
    if target in mutelist:
        say("D: I already am!")
    else:
        mutelist.append(target)
        mutelist.sort()
        json.dump(bot.config, open('config', 'w'), sort_keys=True, indent=2)
        say(":(")
    return


@hook.command(adminonly=True, autohelp=False)
def unmute(inp, input=None, say=None, notice=None, bot=None, config=None):
    """.unmute channel - Makes the bot listen to channel."""
    target = input.chan
    mutelist = bot.config["muted"]
    if target in mutelist:
        mutelist.remove(target)
        mutelist.sort()
        json.dump(bot.config, open('config', 'w'), sort_keys=True, indent=2)
        say(":D <3")
    else:
        say("I am already unmuted.")
    return
