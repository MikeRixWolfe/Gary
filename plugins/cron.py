"""
cron.py: written by MikeFightsBears
"""

import re
import time
import datetime
from util import hook

running_cron_loops = []
timestamp_format = '%I:%M'
datetimemask = '%Y-%m-%d %H:%M'


class EST(datetime.tzinfo):
    def utcoffset(self, dt):
        return datetime.timedelta(hours=-5)
    def dst(self, dt):
        return datetime.timedelta(0)


def localtime(format):
    return time.strftime(format, time.localtime())


def db_init(db):
    db.execute("create table if not exists cron(time, chan, msg, set_by, recurring,"
               " primary key(time, chan, set_by))")
    db.commit()


def get_events(db, time, chan):
    rows = db.execute(
        "select msg, set_by, chan, recurring from cron where time<=? and chan=lower(?)",
        (time, chan.lower())).fetchall()
    return rows or []


def set_event(db, time, chan, msg, set_by, recurring):
    db.execute(
        "insert or replace into cron(time, chan, msg, set_by, recurring) values(?,?,?,?,?)",
        (time, chan.lower(), msg, set_by, recurring))
    db.commit()


def remove_event(db, time, chan, msg, set_by):
    db.execute(
        "delete from cron where time=? and chan=lower(?) and msg=? and set_by=?",
        (time, chan.lower(), msg, set_by))
    db.commit()


def clean_db(db, time, chan):
    db.execute(
        "delete from cron where time<? and chan=lower(?) and recurring!='1'",
        (time, chan.lower()))
    db.commit()


@hook.event('JOIN')
def cron(paraml, nick='', conn=None, db=None):
    global running_cron_loops
    if paraml[0] != '#geekboy' or nick != conn.nick or paraml[0] in running_cron_loops:
        return
    running_cron_loops.append(paraml[0])
    print ">>> u'Beginning cron loop :%s'" % paraml[0]
    db_init(db)
    while True:
        try:
            time.sleep(60)
            datestamp = str(datetime.datetime.now(EST()))[:16]
            rows = get_events(db, datestamp, paraml[0])
            for row in rows:
                conn.send(
                    "PRIVMSG {} :{}".format(paraml[0], "%s: %s" %
                                            (row[1], row[0])))
                if row[3] == False:
                    remove_event(db, datestamp, row[2], row[0], row[1])
            clean_db(db, datestamp, paraml[0])
        except:
            print ">>> u'Error running cron loop :%s'" % paraml[0]


@hook.command()
def remindme(inp, nick='', chan='', db=None):
    ".remindme YYYY-MM-DD HH:MM <message> - Queues <message> to be output at specified date and time."
    db_init(db)
    new_event = re.match(r'(\d\d\d\d-\d\d-\d\d\ \d\d:\d\d)\ (.+)', inp)
    if new_event and new_event.group(1) > str(datetime.datetime.now(EST()))[:16]:
        timestamp = new_event.group(1)
        message = new_event.group(2)

        try:
            set_event(db, timestamp, chan, message, nick, False)
        except:
            return "There was an error inserting your event, please try again later."
        return "Okay, at %s I will remind you of '%s'." % (timestamp, message)
    elif new_event and new_event.group(1) < str(datetime.datetime.now(EST()))[:16]:
        return "Please choose a date/time in the future."
    else:
        return "Please be sure to use the format 'YYYY-MM-DD HH:MM <message>'."
