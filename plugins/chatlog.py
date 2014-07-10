import datetime
import time
from util import hook, timesince, text


@hook.command
def last(inp, nick='', chan='', input=None, db=None, say=None):
    ".last <phrase> - finds the last occurence of a phrase"
    row = db.execute("select time, nick, msg, uts from log where msg like ? "
        "and uts < ? and chan = ? order by uts desc limit 1",
        (('%' + inp.strip() + '%'), (time.time() - 1), chan)).fetchone()
    if row:
        xtime, xnick, xmsg, xuts = row
        say("%s last said \"%s\" on %s (%s ago)" %
            (xnick, xmsg, xtime[:-7], timesince.timesince(xuts)))
    else:
        say("Never!")


@hook.command
def first(inp, chan='', input=None, db=None, say=None):
    ".first <phrase> - finds the first occurence of a phrase"
    row = db.execute("select time, nick, msg, uts from log where msg like ? "
        "and chan = ? order by uts asc limit 1",
        (('%' + inp.strip() + '%'), chan)).fetchone()
    if row:
        xtime, xnick, xmsg, xuts = row
        say("%s first said \"%s\" on %s (%s ago)" %
            (xnick, xmsg, xtime[:-7], timesince.timesince(xuts)))
    else:
        say("Never!")


@hook.command(autohelp=False)
def king(inp, input=None, db=None, say=None, bot=None):
    ".king - gets the user with the most used commands"
    query_string = "select nick, count(nick) as nick_occ from log where ("
    for command in bot.commands.keys():
        query_string += "msg like '." + command + "%' or "
    query_string = query_string.strip('or ')
    query_string = query_string + ") and nick != 'bears' "
    query_string = query_string + \
        "and chan = '%s' group by nick order by nick_occ desc limit 2;" % input.chan
    rows = db.execute(query_string).fetchall()

    if len(rows) == 2:
        say("%s is the king of %s with %s commands. %s is the runner up with %s commands." %
            (rows[0][0], input.conn.nick, rows[0][1], rows[1][0], rows[1][1]))
    elif len(rows) == 1:
        say("%s is the king of %s with %s commands." %
            (rows[0][0], input.conn.nick, rows[0][1]))
    else:
        say("No one has used my commands yet in this channel :(")


@hook.command
def said(inp, chan='', input=None, db=None, say=None):
    ".said <phrase> - finds users who has said a phrase."
    rows = db.execute(
        "select distinct nick from log where msg like ? and chan = ? order by nick",
        ('%' + inp.strip() + '%', chan)).fetchall()
    rows = ([row[0] for row in rows] if rows else None)

    if rows:
        out = ''
        while rows:
            if len(out) + len(rows[0]) + len(str(len(rows))) < 440:
                out += rows.pop(0) + ", "
            else:
                break
        if rows:
            out += "{} others".format(len(rows))
        out = text.rreplace(out.strip(', '), ', ', ', and ', 1)
        say(out + ' have said "{}"'.format(inp))
    else:
        say("No one!")


# def userstats():

# def dailylines():

#def chanstats():

# def dailystats():

# def lines():
