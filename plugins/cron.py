"""
cron.py: written by MikeFightsBears
"""

import re
import time
import datetime
from util import hook

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
    rows = db.execute("select msg, set_by, chan from cron where time=? and chan=lower(?)",
        (time, chan.lower())).fetchall()
    if rows:
        return rows
    else:
        return []


def set_event(db, time, chan, msg, set_by):
    db.execute("insert or replace into cron(time, chan, msg, set_by, recurring) values(?,?,?,?,?)", 
        (time, chan.lower(), msg, set_by, 0))
    db.commit()
    return


def remove_event(db, time, chan, msg, set_by):
    db.execute("delete from cron where time=? and chan=lower(?) and msg=? and set_by=?",
        (time, chan.lower(), msg, set_by))
    db.commit()
    return


def clean_db(db, time, chan):
    db.execute("delete from cron where time<? and chan=lower(?)",
        (time, chan.lower()))
    db.commit()
    return


#@hook.event('JOIN')
@hook.command(autohelp=False, adminonly=True)
def cron(inp, say='', chan='', db=None):
    if chan[0] != '#':
        return
    db_init(db)
    while True:
        datestamp = str(datetime.datetime.now(EST()))[:16]
        rows = get_events(db, datestamp, chan)
        for row in rows:
            say("%s: %s" % (row[1], row[0]))
            #remove_event(db, datestamp, row[2], row[0], row[1])
        clean_db(db, datestamp, chan)
        time.sleep(30)


@hook.event('JOIN')
def blaze(inp, say='', chan=''):
    if chan[0] != '#':
        return
    print ">>> u'Beginning blaze loop :%s'" % chan
    while True:
        timestamp = localtime(timestamp_format)
        if timestamp == '03:20': # my IRC server is in  a different time zone lol
            say("4:20 BLAZE IT!")
        #if str(datetime.datetime.now(EST()))[:16] == 
        time.sleep(60)


@hook.command()
def remindme(inp, nick='', chan='', db=None):
    ".remindme YYYY-MM-DD HH:MM <message> - Queues <message> to be output at specified date and time."
    db_init(db)
    new_event = re.match(r'(\d\d\d\d-\d\d-\d\d\ \d\d:\d\d)\ (.+)', inp)
    if new_event and new_event.group(1) > str(datetime.datetime.now(EST()))[:16]:
        timestamp = new_event.group(1)
        message = new_event.group(2)
        
        try:
            set_event(db, timestamp, chan, message, nick)
        except:
            return "There was an error inserting your event, please try again later."
        return "Okay, at %s I will remind you of '%s'." % (timestamp, message)
    elif new_event and new_event.group(1) < str(datetime.datetime.now(EST()))[:16]:
        return "Please choose a date/time in the future."
    else:
        return "Please be sure to use the format 'YYYY-MM-DD HH:MM <message>'."
