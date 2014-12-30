import json
from util import hook


@hook.command(autohelp=False)
def ignored(inp, notice=None, bot=None, say=None):
    """.ignored - Lists ignored channels/users."""
    ignorelist = bot.config["ignored"]
    if ignorelist:
        return "Ignored channels/users are: %s" % format(", ".join(sorted(ignorelist)))
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
            json.dump(bot.config, open('config', 'w'),
                      sort_keys=True, indent=2)
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
