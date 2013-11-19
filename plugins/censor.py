"""
commands.py: written by MikeFightsBears 2013
"""

import json
from util import hook


@hook.command(adminonly=True)
def censor(inp, say=None, notice=None, bot=None, config=None):
    """.censor <word> - Censors <word>."""
    target = inp

    censorlist = bot.config["censored_strings"]

    if target in censorlist:
        say("%s is already censored." % format(target))
    else:
        say("%s has been censored." % format(target))
        censorlist.append(target)
        censorlist.sort()
        json.dump(bot.config, open('config', 'w'), sort_keys=True, indent=2)
    return


@hook.command(adminonly=True)
def uncensor(inp, say=None, notice=None, bot=None, config=None):
    """.uncensor <word> - Uncensors <word>."""
    target = inp

    censorlist = bot.config["censored_strings"]

    if target in censorlist:
        censorlist.remove(target)
        censorlist.sort()
        json.dump(bot.config, open('config', 'w'), sort_keys=True, indent=2)
        say("%s has been uncensored." % format(target))
    else:
        say("%s is not censored." % format(target))
    return
