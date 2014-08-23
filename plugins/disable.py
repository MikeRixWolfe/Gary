import json
from util import hook


@hook.command(autohelp=False)
def disabled(inp, notice=None, bot=None, say=None):
    """.disabled - Lists disabled commands/plugins."""

    disabled = bot.config["disabled"]

    if disabled:
        say("Disabled commands/plugins are: %s" % format(", ".join(disabled)))
    else:
        say("No commands/plugins are currently disabled.")


@hook.command(adminonly=True)
def disable(inp, say=None, notice=None, bot=None, config=None):
    """.disable <command/plugin> - Disables <command/plugin>."""
    targets = inp.lower().split()

    disabled = bot.config["disabled"]
    skips = []
    new = []
    out = ""

    for target in targets:
        if not target in disabled:
            new.append(target)
            disabled.append(target)
        else:
            skips.append(target)

    if new:
        out = "%s has been disabled. " % format(', '.join(new))
    if skips:
        out += "%s is not enabled." % format(', '.join(skips))

    disabled.sort()
    json.dump(bot.config, open('config', 'w'), sort_keys=True, indent=2)
    say(out)


@hook.command(adminonly=True)
def enable(inp, say=None, notice=None, bot=None, config=None):
    """.enable <command> - Enables <commmand/plugin>."""
    targets = inp.lower().split()

    disabled = bot.config["disabled"]
    skips = []
    new = []
    out = ""

    for target in targets:
        if target in disabled:
            new.append(target)
            disabled.remove(target)
        else:
            skips.append(target)

    if new:
        out = "%s has been enabled. " % format(', '.join(new))
    if skips:
        out += "%s is not disabled." % format(', '.join(skips))

    json.dump(bot.config, open('config', 'w'), sort_keys=True, indent=2)
    say(out)
