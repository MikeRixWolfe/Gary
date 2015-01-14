import json
from util import hook, text


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
        out = text.capitalize_first("{} has been {}. ".format(', '.join(new), name))
    if skips:
        out += text.capitalize_first("{} is already {}.".format(', '.join(skips), name))

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
        out = text.capitalize_first("{} is no longer {}. ".format(', '.join(new), name))
    if skips:
        out += text.capitalize_first("{} was not {}.".format(', '.join(skips), name))

    return out


def config_list(name, config):
    section = config[name]
    return "{}: {}".format(text.capitalize_first(name), ", ".join(section))


@hook.command(autohelp=False)
def disabled(inp, say=None, bot=None):
    """.disabled - Lists disabled commands/plugins."""
    say(config_list("disabled", bot.config))


@hook.command(adminonly=True)
def disable(inp, say=None, bot=None):
    """.disable <command/plugin> - Disables <command/plugin>."""
    say(config_add(inp, "disabled", bot.config))


@hook.command(adminonly=True)
def enable(inp, say=None, bot=None):
    """.enable <command/plugin> - Enables <command/plugin>."""
    say(config_del(inp, "disabled", bot.config))


@hook.command(adminonly=True)
def censor(inp, say=None, bot=None):
    """.censor <word> - Censors <word>."""
    say(config_add(inp, "censored", bot.config))


@hook.command(adminonly=True)
def uncensor(inp, say=None, bot=None):
    """.uncensor <word> - Uncensors <word>."""
    say(config_del(inp, "censored", bot.config))


@hook.command(autohelp=False)
def ignored(inp, say=None, bot=None):
    """.ignored - Lists ignored channel/user/host."""
    say(config_list("ignored", bot.config))


@hook.command(adminonly=True)
def ignore(inp, say=None, bot=None):
    """.ignore <channel|host|nick> - Ignores channel/host/nick."""
    say(config_add(inp, "ignored", bot.config))


@hook.command(adminonly=True)
def unignore(inp, say=None, bot=None):
    """.unignore <channel|host|nick> - Unignores channel/host/nick."""
    say(config_del(inp, "ignored", bot.config))


@hook.command(adminonly=True, autohelp=False)
def mute(inp, chan=None, say=None, bot=None):
    """.mute - Mutes bot in channel."""
    config_add(chan, "muted", bot.config)
    say(":(")


@hook.command(adminonly=True, autohelp=False)
def unmute(inp, chan=None, say=None, bot=None):
    """.unmute - Unmutes bot in channel."""
    config_del(chan, "muted", bot.config)
    say(":D <3")


@hook.command(autohelp=False)
def restricted(inp, say=None, bot=None):
    """.restricted - Lists channels in restricted mode."""
    say(config_list("restricted", bot.config))


@hook.command(adminonly=True, autohelp=False)
def restrict(inp, chan=None, say=None, bot=None):
    """.restrict - Sets current channel to restricted mode."""
    inp = inp or chan
    say(config_add(inp, "restricted", bot.config))


@hook.command(adminonly=True, autohelp=False)
def unrestrict(inp, chan=None, say=None, bot=None):
    """.unrestrict - Removes current channel from restricted mode."""
    inp = inp or chan
    say(config_del(inp, "restricted", bot.config))


@hook.command(autohelp=False)
def opers(inp, say=None, bot=None):
    """.opers - Lists bot opers."""
    say(config_list("opered", bot.config))


@hook.command(adminonly=True)
def oper(inp, say=None, bot=None):
    """.oper <user> - Adds <user> to opers."""
    say(config_add(inp, "opered", bot.config))


@hook.command(adminonly=True)
def deoper(inp, say=None, bot=None):
    """.deoper <user> - Removes <user> from opers."""
    say(config_del(inp, "opered", bot.config))


@hook.command(autohelp=False)
def voicers(inp, say=None, bot=None):
    """.voicers - Lists users with bot voice."""
    say(config_list("voiced", bot.config))


@hook.command(adminonly=True)
def voicer(inp, say=None, bot=None):
    """.voicer <user> - Adds <user> to voicers."""
    say(config_add(inp, "voiced", bot.config))


@hook.command(adminonly=True)
def devoicer(inp, say=None, bot=None):
    """.devoicer <user> - Removes <user> from voicers."""
    say(config_del(inp, "voiced", bot.config))

