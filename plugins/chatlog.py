"""
chatlog.py: written by MikeFightsBears 2013
"""

import datetime
import time
from util import hook

@hook.command
def last(inp, nick='', input=None, db=None, say=None):
    ".last <phrase> - finds the last occurence of a phrase"
    regex_msg = '%'+input.msg[6:]+'%'

    #Long query to overcome the fact that this command has already been logged and would be the last logged instance of the word
    row = db.execute("select * from log where msg like ? and uts = (select max(uts) from log where msg like ? and uts !=  (select max(uts) from log where msg like ?)) and chan = ?",
                (regex_msg, regex_msg, regex_msg, input.chan)).fetchone()
    if row:
        #.strftime("%Y-%m-%d %H:%M:%S"),
        delta = datetime.datetime.now() - datetime.datetime.strptime(row[0],'%Y-%m-%d %H:%M:%S.%f')
        years = delta.days/365
        days=delta.days%365
        hours=delta.seconds/60/60
        minutes=delta.seconds/60%60
        seconds=delta.seconds%60
        if years > 0:
            say("%s last said \"%s\" on %s (%s years, %s days, %s hours, %s minutes, and %s seconds ago)" % (row[2], row[3], row[0][:-7], years, days, hours, minutes, seconds))
        elif days > 0 and years == 0:
            say("%s last said \"%s\" on %s (%s days, %s hours, %s minutes, and %s seconds ago)" % (row[2], row[3], row[0][:-7], days, hours, minutes, seconds))
        elif hours > 0 and days == 0:
            say("%s last said \"%s\" on %s (%s hours, %s minutes, and %s seconds ago)" % (row[2], row[3], row[0][:-7], hours, minutes, seconds))
        elif minutes > 0 and hours == 0:
            say("%s last said \"%s\" on %s (%s minutes, and %s seconds ago)" % (row[2], row[3], row[0][:-7], minutes, seconds))
        else:
            if row[2] == nick:
    	        say("Seriously? You said it like, just now...") 
            else:
    	        say("Seriously? %s said it like, just now..." % row[2])
    else:
        say("Never!")


@hook.command
def first(inp, input=None, db=None, say=None):
    ".first <phrase> - finds the first occurence of a phrase"
    regex_msg = '%'+input.msg[7:]+'%'
    print (regex_msg)
    row = db.execute("select * from log where msg like ? and uts = (select min(uts) from log where msg like ? ) and chan = ?",
                (regex_msg, regex_msg, input.chan)).fetchone()
    if row:
        #.strftime("%Y-%m-%d %H:%M:%S"),
        delta = datetime.datetime.now() - datetime.datetime.strptime(row[0],'%Y-%m-%d %H:%M:%S.%f')
        years = delta.days/365
        days=delta.days%365
        hours=delta.seconds/60/60
        minutes=delta.seconds/60%60
        seconds=delta.seconds%60
        if years > 0:
            say("%s first said \"%s\" on %s (%s years, %s days, %s hours, %s minutes, and %s seconds ago)" % (row[2], row[3], row[0][:-7], years, days, hours, minutes, seconds))
        elif days > 0 and years == 0:
            say("%s first said \"%s\" on %s (%s days, %s hours, %s minutes, and %s seconds ago)" % (row[2], row[3], row[0][:-7], days, hours, minutes, seconds))
        elif hours > 0 and days == 0:
            say("%s first said \"%s\" on %s (%s hours, %s minutes, and %s seconds ago)" % (row[2], row[3], row[0][:-7], hours, minutes, seconds))
        elif minutes > 0 and hours == 0:
            say("%s first said \"%s\" on %s (%s minutes, and %s seconds ago)" % (row[2], row[3], row[0][:-7], minutes, seconds))
        else:
            say("%s first said \"%s\" on %s (%s seconds ago)" % (row[2], row[3], row[0][:-7], seconds))
    else:
        say("Never!")

#@hook.singlethread
@hook.command(autohelp=False)
def king(inp, input=None, db=None, say=None, bot=None):
    ".king - gets the user with the most used commands"
    query_string = "select nick, count(nick) as nick_occ from log where ("
    for command in bot.commands.keys():
        query_string = query_string + "msg like '." + command + "%' or "
    query_string = query_string.strip('or ')
    query_string = query_string + ") and nick != 'bears' "
    query_string = query_string + "and chan = '%s' group by nick order by nick_occ desc limit 2;" % input.chan
    rows = db.execute(query_string).fetchall()

    if len(rows) == 2:
        say("%s is the king of %s with %s commands. %s is the runner up with %s commands." % (rows[0][0], input.conn.nick, rows[0][1], rows[1][0], rows[1][1]))
    elif len(rows) == 1:
        say("%s is the king of %s with %s commands." % (rows[0][0], input.conn.nick, rows[0][1]))
    else:
        say("No one has used my commands yet in this channel :(")

@hook.command
def said(inp, input=None, db=None, say=None):
    ".said <phrase> - finds anywho who has said a phrase"  
    regex_msg = '%'+input.msg[6:]+'%'
    rows = db.execute("select distinct nick from log where msg like ? and chan = ? order by nick",
                (regex_msg,input.chan)).fetchall()
    if rows:
        raw_list = ""
        overflow_counter = 0
        for row in rows:
            return_string = "%s have said %s" % (raw_list[:-2], input.msg[6:])
            if len(regex_msg) + len(return_string) + len(str(overflow_counter)) < 450:
                raw_list += row[0] + ", "
            else:
                overflow_counter += 1
        if overflow_counter == 0 and len(rows) == 1:
            return_string = "%s has said \"%s\"" % (raw_list[:-2], input.msg[6:])
        elif overflow_counter == 0 and len(rows) > 1:
	        return_string = "%s have said \"%s\"" % (raw_list[:-2], input.msg[6:]) 
        else:
	        return_string = "%s%s others have all said \"%s\"" % (raw_list, overflow_counter, input.msg[6:])
        formatted_string = rreplace(return_string, ', ', ', and ', 1)
        say(formatted_string)
    else:
        say("No one!")

def rreplace(s, old, new, occurrence):
    li = s.rsplit(old, occurrence)
    return new.join(li)

#def userstats():

#def dailylines():

#def lines():
