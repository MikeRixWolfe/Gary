" seen.py: written by sklnd in about two beers July 2009"
"	2013.09.24 - modified by MikeFightsBears"

import time

from util import hook, timesince


def db_init(db):
    "check to see that our db has the the seen table and return a connection."
    db.execute("create table if not exists seen(name, time, quote, chan, "
                 "primary key(name, chan))")
    db.commit()


@hook.command(autohelp=False)
def around(inp, nick='', chan='', say='',  db=None, input=None):
    ".around [minutes] - Lists what nicks have been active in the last [minutes] minutes, defaults to 15"
    
    db_init(db)

    minutes=15

    if inp.strip().isdigit():
        minutes = int(inp.strip())

    period = time.time()-(minutes*60)

    rows = db.execute("select name  from seen where time >= "
                           " ? and chan = ? order by name", (period,chan)).fetchall()

    if rows:
        raw_list=""
        overflow_counter = 0
        for row in rows:
            return_string = "Users around in the last %s minutes: %s" % (minutes, raw_list[:-2])
            if len("Users around in the last  minutes: ") + len(str(minutes))+ len(return_string) + len(str(overflow_counter)) < 460:
                raw_list += row[0] + ", "
            else:
                overflow_counter += 1
        if overflow_counter == 0:
            return_string = "Users around in the last %s minutes: %s" % (minutes, raw_list[:-2])
        else:
            return_string = "Users around in the last %s minutes: %s%s others." % (minutes, raw_list, overflow_counter)

        formatted_string = rreplace(return_string, ', ', ', and ', 1)

        say(formatted_string)
    else:
        say("No one!")

def rreplace(s, old, new, occurrence):
    li = s.rsplit(old, occurrence)
    return new.join(li)




@hook.command
def seen(inp, nick='', chan='', db=None, input=None):
    ".seen <nick> - Tell when a nickname was last in active in irc"

    if input.conn.nick.lower() == inp.lower():
        # user is looking for us, being a smartass
        return "You need to get your eyes checked."

    if inp.lower() == nick.lower():
        return "Have you looked in a mirror lately?"

    db_init(db)

    last_seen = db.execute("select name, time, quote from seen where name"
                           " like ? and chan = ?", (inp, chan)).fetchone()

    if last_seen:
        reltime = timesince.timesince(last_seen[1])
        if last_seen[0] != inp.lower():  # for glob matching
            inp = last_seen[0]
        if last_seen[2][0:1]=="\x01":
            return '%s was last seen %s ago: *"%s %s*"' % \
                    (inp, reltime, inp, last_seen[2][8:-1])
        else:
            return '%s was last seen %s ago saying: "%s"' % \
                    (inp, reltime, last_seen[2])
    else:
        return "I've never seen %s" % inp
