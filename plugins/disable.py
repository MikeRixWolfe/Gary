import json
from util import hook


@hook.command(autohelp=False)
def disabled(inp, notice=None, bot=None, say=None):
    """.disabled - Lists disabled commands/plugins"""

    disabled = bot.config["disabled"]

    if disabled:
        say("Disabled commands/plugins are: %s" % format(", ".join(disabled)))
    else:
        say("No commands/plugins are currently disabled.")
    return


@hook.command(adminonly=True)
def disable(inp, say=None, notice=None, bot=None, config=None):
    """.disable <command/plugin> - Disables <command/plugin>."""
    target = inp.lower()

    disabled = bot.config["disabled"]

    if target in disabled:
        say("%s is already disabled." % format(target))
    else:
        say("%s has been disabled." % format(target))
        disabled.append(target)
        disabled.sort()
        json.dump(bot.config, open('config', 'w'), sort_keys=True, indent=2)
    return


@hook.command(adminonly=True)
def enable(inp, say=None, notice=None, bot=None, config=None):
    """.enable <command> - Enables <commmand/plugin>."""
    target = inp.lower()

    disabled = bot.config["disabled"]

    if target in disabled:
        say("%s has been enabled." % format(target))
        disabled.remove(target)
        disabled.sort()
        json.dump(bot.config, open('config', 'w'), sort_keys=True, indent=2)
    else:
        say("%s is not disabled." % format(target))
    return
