"""
plugins.py: written by MikeFightsBears 2013
"""

import json
from util import hook


@hook.command(autohelp=False)
def disabled_plugins(inp, notice=None, bot=None, say=None):
    """.disabled_plugins - Lists disabled plugins"""

    pluginlist = bot.config["disabled_plugins"]

    if pluginlist:
        say("Disabled plugins are: %s" % format(", ".join(pluginlist)))
    else:
        say("No plugins are currently disabled.")
    return


@hook.command(adminonly=True)
def disable_plugin(inp, say=None, notice=None, bot=None, config=None):
    ".disable_plugin <plugin> - Disables <plugin>."
    target = inp.lower()

    pluginlist = bot.config["disabled_plugins"]

    if target in pluginlist:
        say("%s is already disabled." % format(target))
    else:
        say("%s has been disabled." % format(target))
	pluginlist.append(target)
	pluginlist.sort()
        json.dump(bot.config, open('config', 'w'), sort_keys=True, indent=2)
    return


@hook.command(adminonly=True)
def enable_plugin(inp, say=None, notice=None, bot=None, config=None):
    ".enable_plugin <plugin> - Enables <plugin>."

    target = inp.lower()

    pluginlist = bot.config["disabled_plugins"]

    if target in pluginlist:
        say("%s has been enabled." % format(target))
        pluginlist.remove(target)
        pluginlist.sort()
        json.dump(bot.config, open('config', 'w'), sort_keys=True, indent=2)
    else:
        say("%s is not disabled." % format(target))
    return
