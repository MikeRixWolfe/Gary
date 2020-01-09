import json
from util import hook, text


@hook.command(adminonly=True, autohelp=False)
def suggestions(inp, bot=None):
    """.suggestions - Toggles fuzzy matching suggestions for mistyped commands."""
    if bot.config.get("suggestions", True):
        bot.config["suggestions"] = False
        json.dump(bot.config, open('config', 'w'), sort_keys=True, indent=2)
        return "Command suggestions are now disabled."
    else:
        bot.config["suggestions"] = True
        json.dump(bot.config, open('config', 'w'), sort_keys=True, indent=2)
        return "Command suggestions are now enabled."


def config_add(items, name, config):
    out = ""
    new = []
    skips = []
    section = config.get(name, None)
    items = items.lower().split()

    for item in items:
        if not item in section:
            new.append(item)
            section.append(item)
        else:
            skips.append(item)

    section.sort()
    json.dump(config, open('config', 'w'), sort_keys=True, indent=2)

    if new:
        out = "{} has been {}.".format(', '.join(new), name)
    if skips:
        out += "{} is already {}.".format(', '.join(skips), name)

    return out


def config_del(items, name, config):
    out = ""
    new = []
    skips = []
    section = config.get(name, None)
    items = items.lower().split()

    for item in items:
        if item in section:
            new.append(item)
            section.remove(item)
        else:
            skips.append(item)

    section.sort()
    json.dump(config, open('config', 'w'), sort_keys=True, indent=2)

    if new:
        verb = "are" if len(new) > 1 else "is"
        out = "{} {} no longer {}.".format(', '.join(new), verb, name)
    if skips:
        verb = "were" if len(skips) > 1 else "was"
        out += "{} {} not {}.".format(', '.join(skips), verb, name)

    return out


def config_list(name, config):
    section = config[name]
    return "{}: {}".format(text.capitalize_first(name), ", ".join(section))


@hook.command(autohelp=False, modonly=True)
def disabled(inp, say=None, bot=None):
    """disabled - Lists disabled commands/plugins."""
    say(config_list("disabled", bot.config))


@hook.command(modonly=True)
def disable(inp, say=None, bot=None):
    """disable <command/plugin> - Disables <command/plugin>."""
    say(config_add(inp, "disabled", bot.config))


@hook.command(modonly=True)
def enable(inp, say=None, bot=None):
    """enable <command/plugin> - Enables <command/plugin>."""
    say(config_del(inp, "disabled", bot.config))


@hook.command(modonly=True)
def censor(inp, say=None, bot=None):
    """censor <word> - Censors <word>."""
    say(config_add(inp, "censored", bot.config))


@hook.command(modonly=True)
def uncensor(inp, say=None, bot=None):
    """uncensor <word> - Uncensors <word>."""
    say(config_del(inp, "censored", bot.config))


@hook.command(autohelp=False, modonly=True)
def ignored(inp, say=None, bot=None):
    """ignored - Lists ignored channel/user/host."""
    say(config_list("ignored", bot.config))


@hook.command(modonly=True)
def ignore(inp, say=None, bot=None):
    """ignore <channel|host|nick> - Ignores channel/host/nick."""
    say(config_add(inp, "ignored", bot.config))


@hook.command(modonly=True)
def unignore(inp, say=None, bot=None):
    """unignore <channel|host|nick> - Unignores channel/host/nick."""
    say(config_del(inp, "ignored", bot.config))


@hook.command(modonly=True, autohelp=False)
def mute(inp, chan=None, say=None, bot=None):
    """mute - Mutes bot in channel."""
    config_add(chan, "muted", bot.config)
    say(":(")


@hook.command(modonly=True, autohelp=False)
def unmute(inp, chan=None, say=None, bot=None):
    """unmute - Unmutes bot in channel."""
    config_del(chan, "muted", bot.config)
    say(":D <3")


@hook.command(autohelp=False, modonly=True)
def restricted(inp, say=None, bot=None):
    """restricted - Lists channels in restricted mode."""
    say(config_list("restricted", bot.config))


@hook.command(modonly=True, autohelp=False)
def restrict(inp, chan=None, say=None, bot=None):
    """restrict - Sets current channel to restricted mode."""
    inp = inp or chan
    say(config_add(inp, "restricted", bot.config))


@hook.command(modonly=True, autohelp=False)
def unrestrict(inp, chan=None, say=None, bot=None):
    """unrestrict - Removes current channel from restricted mode."""
    inp = inp or chan
    say(config_del(inp, "restricted", bot.config))


@hook.command(autohelp=False)
def moded(inp, say=None, bot=None):
    """moded - Lists bot moderators."""
    say(config_list("moded", bot.config))


@hook.command(adminonly=True)
def mod(inp, say=None, bot=None):
    """mod <user> - Adds a user as a bot moderators."""
    say(config_add(inp, "moded", bot.config))


@hook.command(adminonly=True)
def demod(inp, say=None, bot=None):
    """demod <user> - Removes a user as a bot moderator."""
    say(config_del(inp, "moded", bot.config))


@hook.command(autohelp=False, modonly=True)
def allowed(inp, say=None, bot=None):
    """allowed - Lists users allowed to interact with the bot in restricted channels."""
    say(config_list("allowed", bot.config))


@hook.command(modonly=True)
def allow(inp, say=None, bot=None):
    """allow <user> - Allows a user to interact with the bot in restricted channels."""
    say(config_add(inp, "allowed", bot.config))


@hook.command(modonly=True)
def disallow(inp, say=None, bot=None):
    """disallow <user> - Disallows a user to interact with the bot in restricted channels."""
    say(config_del(inp, "allowed", bot.config))

