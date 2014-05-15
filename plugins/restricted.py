import json
from util import hook


@hook.command(adminonly=True, autohelp=False)
def restrict(inp, input=None, say=None, bot=None):
    """.restrict - Sets current channel to restricted mode."""
    target = input.chan
    chans = bot.config["restrictedmode"]
    if target in chans:
        say("%s is already in restricted mode." % input.chan)
    else:
        chans.append(target)
        chans.sort()
        json.dump(bot.config, open('config', 'w'), sort_keys=True, indent=2)
        say("Restricted mode activated for %s." % input.chan)
    return


@hook.command(adminonly=True, autohelp=False)
def unrestrict(inp, input=None, say=None, bot=None):
    """.unrestrict - Removes current channel from restricted mode"""
    target = input.chan
    chans = bot.config["restrictedmode"]
    if target in chans:
        chans.remove(target)
        chans.sort()
        json.dump(bot.config, open('config', 'w'), sort_keys=True, indent=2)
        say("Restricted mode deactivated for %s." % input.chan)
    else:
        say("%s is not in restricted mode." % input.chan)
    return


@hook.command(autohelp=False)
def restricted(inp, bot=None, say=None):
    """.restricted - Lists channels in restricted mode."""
    chans = bot.config["restrictedmode"]
    if chans:
        say("Channels in restricted mode are: %s" % format(", ".join(chans)))
    else:
        say("No channels are currently in restricted mode.")
    return


@hook.command(autohelp=False)
def opers(inp, bot=None, say=None):
    """.opers - Lists bot opers."""
    opers = bot.config["opers"]
    admins = bot.config["admins"]
    allows = admins + opers
    if allows:
        say("Bot operators are: %s" % format(", ".join(allows)))
    else:
        say("There are currently no bot operators.")
    return


@hook.command(adminonly=True)
def oper(inp, say=None, bot=None):
    """.oper user - Adds user to opers."""
    target = inp.lower()
    opers = bot.config["opers"]
    admins = bot.config["admins"]
    allows = admins + opers
    if target in allows:
        return "%s is already a bot operator." % format(target)
    else:
        opers.append(target)
        opers.sort()
        json.dump(bot.config, open('config', 'w'), sort_keys=True, indent=2)
        say("%s +o" % format(target))
    return


@hook.command(adminonly=True)
def deoper(inp, say=None, bot=None):
    """.deoper <user> - Removes user from opers."""
    target = inp.lower()
    opers = bot.config["opers"]
    admins = bot.config["admins"]
    allows = admins + opers
    if target in opers:
        opers.remove(target)
        opers.sort()
        json.dump(bot.config, open('config', 'w'), sort_keys=True, indent=2)
        say("%s -o" % format(target))
    else:
        if target in admins:
            return "You can not remove bot admins as bot operators."
        return "%s is not a bot operator." % format(target)
    return


@hook.command(autohelp=False)
def voicers(inp, bot=None, say=None):
    """.voicers - Lists users with bot voice."""
    voicers = bot.config["voice"]
    opers = bot.config["opers"]
    admins = bot.config["admins"]
    allows = admins + opers + voicers
    if allows:
        return "Users with bot voice are: %s" % format(", ".join(allows))
    else:
        say("There are currently no users with bot voice.")
    return


@hook.command(adminonly=True)
def voicer(inp, say=None, bot=None):
    """.voicer user - Adds user to voicers."""
    targets = inp.lower().split()
    voicers = bot.config["voice"]
    opers = bot.config["opers"]
    admins = bot.config["admins"]
    mergelist = voicers + opers + admins
    skips = []
    newvoicers = []
    for target in targets:
        if target not in mergelist:
            newvoicers.append(target)
            voicers.append(target)
        else:
            skips.append(target)
    voicers.sort()
    json.dump(bot.config, open('config', 'w'), sort_keys=True, indent=2)
    if len(newvoicers) == 0:
        return "%s already has bot voice." % format(", ".join(skips))
    say("%s +v" % format(", ".join(newvoicers)))


@hook.command(adminonly=True)
def devoicer(inp, say=None, bot=None):
    """.devoicer <user> - Removes user from voicers."""
    targets = inp.lower().split()
    voicers = bot.config["voice"]
    opers = bot.config["opers"]
    admins = bot.config["admins"]
    skips = []
    oldvoicers = []
    for target in targets:
        if target not in admins and target not in opers:
            if target in voicers:
                oldvoicers.append(target)
                voicers.remove(target)
            else:
                skips.append(target)
    voicers.sort()
    json.dump(bot.config, open('config', 'w'), sort_keys=True, indent=2)

    if len(oldvoicers) == 0:
        if len(skips) == 0:
            return "You can not remove bot admins or opers as bot voicers."
        return "%s does not have bot voice." % format(", ".join(skips))
    else:
        say("%s -v" % format(", ".join(oldvoicers)))
    return
