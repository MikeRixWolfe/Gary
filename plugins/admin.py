from util import hook, text
import os
import sys
import re
import json
import time
import signal
import subprocess


@hook.command("quit", autohelp=False, adminonly=True)
@hook.command(autohelp=False, adminonly=True)
def stop(inp, nick=None, conn=None):
    """.stop [reason] - Kills the bot with [reason] as its quit message."""
    if inp:
        conn.cmd("QUIT", ["Killed by {} ({})".format(nick, inp)])
    else:
        conn.cmd("QUIT", ["Killed by {}.".format(nick)])
    time.sleep(5)
    os.kill(os.getpid(), signal.SIGTERM)


@hook.command(autohelp=False, adminonly=True)
def restart(inp, nick=None, conn=None, bot=None):
    """.restart [reason] - Restarts the bot with [reason] as its quit message."""
    for botcon in bot.conns:
        if inp:
            bot.conns[botcon].cmd(
                "QUIT", ["Restarted by {} ({})".format(nick, inp)])
        else:
            bot.conns[botcon].cmd("QUIT", ["Restarted by {}.".format(nick)])
    time.sleep(5)
    args = sys.argv[:]
    args.insert(0, sys.executable)
    os.execv(sys.executable, args)


@hook.command(adminonly=True)
def join(inp, conn=None, notice=None):
    """.join <channel> - Joins <channel>."""
    notice("Attempting to join {}...".format(inp))
    conn.send("JOIN " + inp)


@hook.command(adminonly=True)
def connect(inp, conn=None, notice=None):
    """.connect <channel> - Joins <channel>."""
    notice("Attempting to connect to {}...".format(inp))
    conn.send("CONNECT " + inp)


@hook.command(autohelp=False, adminonly=True)
def part(inp, conn=None, chan=None, notice=None):
    """.part <channel> - Leaves <channel>. If [channel] is blank the bot will leave the channel the command was used in."""
    if inp:
        target = inp
    else:
        target = chan
    notice("Attempting to leave {}...".format(target))
    conn.send("PART " + target)


@hook.command(autohelp=False, adminonly=True)
def cycle(inp, conn=None, chan=None, notice=None):
    """.cycle <channel> - Cycles <channel>. If [channel] is blank the bot will cycle the channel the command was used in."""
    if inp:
        target = inp
    else:
        target = chan
    notice("Attempting to cycle {}...".format(target))
    conn.send("PART " + target)
    conn.send("JOIN " + target)


@hook.command(adminonly=True)
def nick(inp, notice=None, conn=None):
    """.nick <nick> - Changes the bots nickname to <nick>."""
    if not re.match("^[A-Za-z0-9_|.-\]\[]*$", inp.lower()):
        notice("Invalid username!")
        return
    notice("Attempting to change nick to \"{}\"...".format(inp))
    conn.set_nick(inp)


@hook.command(adminonly=True)
def raw(inp, conn=None, notice=None):
    """.raw <command> - Sends a RAW IRC command."""
    notice("Raw command sent.")
    conn.send(inp)


def mode_cmd(mode, text, inp, chan, conn, notice):
    """.mode [channel] <target> <mode> - Generic mode setting function."""
    split = inp.split(" ")
    if split[0].startswith("#"):
        channel = split[0]
        target = split[1]
        notice("Attempting to {} {} in {}...".format(text, target, channel))
        conn.send("MODE {} {} {}".format(channel, mode, target))
    else:
        channel = chan
        target = split[0]
        notice("Attempting to {} {} in {}...".format(text, target, channel))
        conn.send("MODE {} {} {}".format(channel, mode, target))


def mode_cmd_no_target(mode, text, inp, chan, conn, notice):
    """.mode [channel] <mode> - Generic mode setting function without a target."""
    split = inp.split(" ")
    if split[0].startswith("#"):
        channel = split[0]
        notice("Attempting to {} {}...".format(text, channel))
        conn.send("MODE {} {}".format(channel, mode))
    else:
        channel = chan
        notice("Attempting to {} {}...".format(text, channel))
        conn.send("MODE {} {}".format(channel, mode))


@hook.command(adminonly=True)
def ban(inp, conn=None, chan=None, notice=None):
    """.ban [channel] <user> - Makes the bot ban <user> in [channel]. If [channel] is blank the bot will ban <user> in the channel the command was used in."""
    mode_cmd("+b", "ban", inp, chan, conn, notice)


@hook.command(adminonly=True)
def unban(inp, conn=None, chan=None, notice=None):
    """.unban [channel] <user> - Makes the bot unban <user> in [channel]. If [channel] is blank the bot will unban <user> in the channel the command was used in."""
    mode_cmd("-b", "unban", inp, chan, conn, notice)


@hook.command(adminonly=True)
def quiet(inp, conn=None, chan=None, notice=None):
    """.quiet [channel] <user> - Makes the bot quiet <user> in [channel]. If [channel] is blank the bot will quiet <user> in the channel the command was used in."""
    mode_cmd("+q", "quiet", inp, chan, conn, notice)


@hook.command(adminonly=True)
def unquiet(inp, conn=None, chan=None, notice=None):
    """.unquiet [channel] <user> - Makes the bot unquiet <user> in [channel]. If [channel] is blank the bot will unquiet <user> in the channel the command was used in."""
    mode_cmd("-q", "unquiet", inp, chan, conn, notice)


@hook.command(adminonly=True)
def voice(inp, conn=None, chan=None, notice=None):
    """.voice [channel] <user> - Makes the bot voice <user> in [channel]. If [channel] is blank the bot will voice <user> in the channel the command was used in."""
    mode_cmd("+v", "voice", inp, chan, conn, notice)


@hook.command(adminonly=True)
def devoice(inp, conn=None, chan=None, notice=None):
    """.devoice [channel] <user> - Makes the bot devoice <user> in [channel]. If [channel] is blank the bot will devoice <user> in the channel the command was used in."""
    mode_cmd("-v", "devoice", inp, chan, conn, notice)


@hook.command(adminonly=True)
def op(inp, conn=None, chan=None, notice=None):
    """.op [channel] <user> - Makes the bot op <user> in [channel]. If [channel] is blank the bot will op <user> in the channel the command was used in."""
    mode_cmd("+o", "op", inp, chan, conn, notice)


@hook.command(adminonly=True)
def deop(inp, conn=None, chan=None, notice=None):
    """.deop [channel] <user> - Makes the bot deop <user> in [channel]. If [channel] is blank the bot will deop <user> in the channel the command was used in."""
    mode_cmd("-o", "deop", inp, chan, conn, notice)


@hook.command(adminonly=True)
def topic(inp, conn=None, chan=None):
    """.topic [channel] <topic> - Change the topic of a channel."""
    split = inp.split(" ")
    if split[0].startswith("#"):
        message = " ".join(split[1:])
        chan = split[0]
        out = "TOPIC {} :{}".format(chan, message)
    else:
        message = " ".join(split)
        out = "TOPIC {} :{}".format(chan, message)
    conn.send(out)


@hook.command(adminonly=True)
def kick(inp, chan=None, conn=None, notice=None):
    """.kick [channel] <user> [reason] - Makes the bot kick <user> in [channel]. If [channel] is blank the bot will kick the <user> in the channel the command was used in."""
    split = inp.split(" ")

    if split[0].startswith("#"):
        channel = split[0]
        target = split[1]
        if len(split) > 2:
            reason = " ".join(split[2:])
            out = "KICK {} {}: {}".format(channel, target, reason)
        else:
            out = "KICK {} {}".format(channel, target)
    else:
        channel = chan
        target = split[0]
        if len(split) > 1:
            reason = " ".join(split[1:])
            out = "KICK {} {} :{}".format(channel, target, reason)
        else:
            out = "KICK {} {}".format(channel, target)

    notice("Attempting to kick {} from {}...".format(target, channel))
    conn.send(out)


@hook.command(adminonly=True)
def remove(inp, chan=None, conn=None):
    """.remove [channel] [user] - Force a user to part from a channel."""
    split = inp.split(" ")
    if split[0].startswith("#"):
        message = " ".join(split[1:])
        chan = split[0]
        out = "REMOVE {} :{}".format(chan, message)
    else:
        message = " ".join(split)
        out = "REMOVE {} :{}".format(chan, message)
    conn.send(out)


@hook.command(adminonly=True, autohelp=False)
def mutechan(inp, conn=None, chan=None, notice=None):
    """.mute [channel] - Makes the bot mute a channel. If [channel] is blank the bot will mute the channel the command was used in."""
    mode_cmd_no_target("+m", "mute", inp, chan, conn, notice)


@hook.command(adminonly=True, autohelp=False)
def unmutechan(inp, conn=None, chan=None, notice=None):
    """.mute [channel] - Makes the bot mute a channel. If [channel] is blank the bot will mute the channel the command was used in."""
    mode_cmd_no_target("-m", "unmute", inp, chan, conn, notice)


@hook.command(adminonly=True, autohelp=False)
def lock(inp, conn=None, chan=None, notice=None):
    """.lock [channel] - Makes the bot lock a channel. If [channel] is blank the bot will mute the channel the command was used in."""
    mode_cmd_no_target("+i", "lock", inp, chan, conn, notice)


@hook.command(adminonly=True, autohelp=False)
def unlock(inp, conn=None, chan=None, notice=None):
    """.unlock [channel] - Makes the bot unlock a channel. If [channel] is blank the bot will mute the channel the command was used in."""
    mode_cmd_no_target("-i", "unlock", inp, chan, conn, notice)


@hook.command(adminonly=True)
def say(inp, conn=None, chan=None):
    """.say [channel] <message> - Makes the bot say <message> in [channel]. If [channel] is blank the bot will say the <message> in the channel
    the command was used in."""
    split = inp.split(" ")
    if split[0][0] == "#":
        message = " ".join(split[1:])
        out = "PRIVMSG {} :{}".format(split[0], message)
    else:
        message = " ".join(split[0:])
        out = "PRIVMSG {} :{}".format(chan, message)
    conn.send(out)


@hook.command(adminonly=True)
def rsay(inp, conn=None, chan=None):
    """.say [channel] <message> - Makes the bot say <message> in [channel]. If [channel] is blank the bot will
    the command was used in."""
    split = inp.split(" ")
    if split[0][0] == "#":
        message = text.rainbow(" ".join(split[1:]))
        out = "PRIVMSG {} :{}".format(split[0], message)
    else:
        message = text.rainbow(" ".join(split[0:]))
        out = "PRIVMSG {} :{}".format(chan, message)
    conn.send(out)


hook.command(adminonly=True)
def action(inp, conn=None, chan=None):
    """.action [channel] <action> - Makes the bot do <action> in [channel]. If [channel] is blank the bot will say the <action> in the channel the command was used in."""
    inp = inp.split(" ")
    if inp[0][0] == "#":
        message = " ".join(inp[1:])
        out = "PRIVMSG {} :{}".format(inp[0], message)
    else:
        message = " ".join(inp[0:])
        out = "PRIVMSG {} :{}".format(chan, message)
    conn.action(chan, message)


@hook.command(adminonly=True)
def me(inp, conn=None, chan=None):
    """.me [channel] <action> - Makes the bot act out <action> in [channel]. If [channel] is blank the bot will act the <action> in the channel the command was used in."""
    inp = inp.split(" ")
    if inp[0][0] == "#":
        message = ""
        for x in inp[1:]:
            message = message + x + " "
        message = message[:-1]
        out = "PRIVMSG {} :\x01ACTION {}\x01".format(inp[0], message)
    else:
        message = ""
        for x in inp[0:]:
            message = message + x + " "
        message = message[:-1]
        out = "PRIVMSG {} :\x01ACTION {}\x01".format(chan, message)
    conn.send(out)


@hook.command(adminonly=True)
def pm(inp, conn=None, chan=None):
    """.say [channel] <message> - Makes the bot say <message> in [channel]. If [channel] is blank the bot will say the <message> in the channel the command was used in."""
    inp = inp.split(" ")
    if len(inp) > 1:
        message = " ".join(inp[1:])
        out = "PRIVMSG {} :{}".format(inp[0], message)
    else:
        message = " ".join(inp[0:])
        out = "PRIVMSG {} :{}".format(chan, message)
    conn.send(out)
