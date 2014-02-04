"""
seen.py - written by MikeFightsBears 2013
"""

import time
from util import hook, timesince


def rreplace(s, old, new, occurrence):
    li = s.rsplit(old, occurrence)
    return new.join(li)


@hook.command(autohelp=False)
def around(inp, nick='', chan='', say='', db=None, input=None):
    ".around [minutes] - Lists what nicks have been active in the last [minutes] minutes, defaults to 15"
    minutes = 15
    if inp.strip().isdigit():
        minutes = int(inp.strip())
    period = time.time() - (minutes * 60)
    rows = db.execute("select nick from seen where time >= "
                      " ? and chan = ? order by nick", (period, chan)).fetchall()

    if rows:
        raw_list = ""
        overflow_counter = 0
        for row in rows:
            return_string = "Users around in the last %s minutes: %s" % (
                minutes, raw_list[:-2])
            if len("Users around in the last  minutes: ") + len(str(minutes)) + len(return_string) + len(str(overflow_counter)) < 460:
                raw_list += row[0] + ", "
            else:
                overflow_counter += 1
        if overflow_counter == 0:
            return_string = "Users around in the last %s minutes: %s" % (
                minutes, raw_list[:-2])
        else:
            return_string = "Users around in the last %s minutes: %s%s others." % (
                minutes, raw_list, overflow_counter)
        formatted_string = rreplace(return_string, ', ', ', and ', 1)
        say(formatted_string)
    else:
        say("No one!")


@hook.command
def seen(inp, nick='', chan='', db=None, input=None):
    ".seen <nick> - Tell when a nickname was last in active in irc"
    if input.conn.nick.lower() == inp.lower():
        return "You need to get your eyes checked."
    if inp.lower() == nick.lower():
        return "Have you looked in a mirror lately?"

    last_seen = db.execute("select nick, uts, msg, action, chan, time from seen where nick"
                           " like ? and chan = ? and server = ?", (inp.lower(), chan,
                           input.server)).fetchone()

    if last_seen:
        reltime = timesince.timesince(last_seen[1])
        if last_seen[3] == 'PRIVMSG':
            return '%s was last seen %s ago saying "%s" [%s]' % \
                (last_seen[0], reltime, last_seen[2], last_seen[5])
        elif last_seen[3] == 'JOIN':
            return '%s was last seen %s ago joining %s [%s]' % \
                (last_seen[0], reltime, last_seen[4], last_seen[5])
        elif last_seen[3] == 'PART':
            return '%s was last seen %s ago leaving %s [%s]' % \
                (last_seen[0], reltime, last_seen[4], last_seen[5])
        elif last_seen[3] == 'KICK':
            return '%s was last seen %s ago being kicked from %s [%s]' % \
                (last_seen[0], reltime, last_seen[4], last_seen[5])
    else:
        return "I've never seen %s" % inp
