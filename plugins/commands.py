"""
commands.py: written by MikeFightsBears 2013
"""

import json
from util import hook


@hook.command(autohelp=False)
def disabled_commands(inp, notice=None, bot=None, say=None):
    """.disabled_commands - Lists disabled commands"""

    commandlist = bot.config["disabled_commands"]

    if commandlist:
        say("Disabled commands are: %s" % format(", ".join(commandlist)))
    else:
        say("No commands are currently disabled.")
    return


@hook.command(adminonly=True)
def disable_command(inp, say=None, notice=None, bot=None, config=None):
    """.disable_command <command> - Disables <command>."""
    target = inp.lower()

    commandlist = bot.config["disabled_commands"]

    if target in commandlist:
        say("%s is already disabled." % format(target))
    else:
        say("%s has been diabled." % format(target))
        commandlist.append(target)
        commandlist.sort()
        json.dump(bot.config, open('config', 'w'), sort_keys=True, indent=2)
    return


@hook.command(adminonly=True)
def enable_command(inp, say=None, notice=None, bot=None, config=None):
    """.enable_command <command> - Enables <commmand>."""
    target = inp.lower()

    commandlist = bot.config["disabled_commands"]

    if target in commandlist:
        say("%s has been enabled." % format(target))
        commandlist.remove(target)
        commandlist.sort()
        json.dump(bot.config, open('config', 'w'), sort_keys=True, indent=2)
    else:
        say("%s is not disabled." % format(target))
    return
