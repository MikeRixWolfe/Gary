import re
import time
from datetime import datetime
from util import hook


def db_init(db):
    db.execute("create table if not exists cron(time, chan, msg, set_by,"
        " primary key(time, chan, set_by))")
    db.commit()


def get_events(db, time):
    rows = db.execute("select msg, set_by, chan from cron where time<=?",
        (time,)).fetchall()
    return rows or []


def set_event(db, time, chan, msg, set_by):
    db.execute("insert or replace into cron(time, chan, msg, set_by)"
        " values(?,?,?,?)", (time, chan.lower(), msg, set_by))
    db.commit()


def clean_db(db, time):
    db.execute("delete from cron where time<=?", (time,))
    db.commit()


@hook.singlethread
@hook.event('JOIN')
def cron(paraml, nick='', conn=None, db=None):
    if paraml[0] != '#geekboy' or nick != conn.nick:
        return
    time.sleep(1)  # Allow chan list time to update
    print ">>> u'Beginning cron loop :{}'".format(paraml[0])
    db_init(db)
    while paraml[0] in conn.channels:
        try:
            time.sleep(30)
            datestamp = str(datetime.now())[:16]
            rows = get_events(db, datestamp)
            for row in rows:
                conn.send("PRIVMSG {} :{}".format(row[2],
                    "%s: %s" % (row[1], row[0])))
            clean_db(db, datestamp)
        except Exception as e:
            print ">>> u'Error running cron loop :{}'".format(e)
    print ">>> u'Ending cron loop :{}'".format(paraml[0])


@hook.command()
def remindme(inp, nick='', chan='', db=None):
    """.remindme YYYY-MM-DD HH:MM <message> - Queues <message> to be output at specified date and time."""
    db_init(db)
    new_event = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2})\ (.+)', inp)
    if new_event and new_event.group(1) > str(datetime.now())[:16]:
        timestamp, message = new_event.groups()
        try:
            set_event(db, timestamp, chan, message, nick)
        except:
            return "There was an error inserting your event, please try again in a few minutes."
        return "Okay, I'll remind you."
    elif new_event and new_event.group(1) <= str(datetime.now())[:16]:
        return "Please choose a date/time in the future."
    else:
        return "Please be sure to use the format 'YYYY-MM-DD HH:MM <message>'."
