"""
karma.py: written by MikeFightsBears 2013
"""

from util import hook


def db_init(db):
    db.execute("create table if not exists karma(chan, word, karma,"
               " primary key(chan, word))")
    db.commit()


def get_karma(db, chan, word):
    row = db.execute("select karma from karma where chan=? and word=lower(?)",
                     (chan, word)).fetchone()
    if row:
        return row[0]
    else:
        return 0


@hook.singlethread
@hook.regex(r'([^ ^\(^(\)\+\+)^(\)--)]+((\+\+)|(--))|\([^\(^(\)\+\+$)^(\)--)]+\)((\+\+)|(--)))')
def karma_edit(inp, chan='', nick='', say=None, db=None):
    db_init(db)
    word = inp.group(1)[:-2].strip('() ')
    if word.lower() == nick.lower():
        say("Please do not karma yourself.")
    else:
        karma = int(get_karma(db, chan, word))
        delta = inp.group(1)[-2:].strip()
        if delta == "++":
            karma = karma + 1
        elif delta == "--":
            karma = karma - 1
        else:
            karma = karma
        db.execute("insert or replace into karma(chan, word, karma)"
                   "values(?,?,?)", (chan, word.lower(), karma))
        db.commit()


@hook.singlethread
@hook.command
def karma(inp, chan='', say=None, db=None, input=None):
    ".karma <word> - returns karma of <word>; <word>(+ +|- -) - increments or decrements karma of <word> (no space)"
    db_init(db)
    karma = get_karma(db, chan, inp.strip('()? '))

    if karma:
        say("%s has %s karma" % (inp.strip('()? '), karma))
    else:
        say("%s has neutral karma" % inp.strip('()? '))


@hook.singlethread
@hook.regex(r'^(.+)(?: has an all-time net karma of )(-)?(\d+)(?:\ .+)?')
def setkarma(inp, nick='', chan='', db=None):
    db_init(db)
    word = inp.group(1)
    karma = int(inp.group(3))
    if inp.group(2) != None:
        karma = -karma
    karma_from_db = int(get_karma(db, chan, word))
    if nick != "extrastout":
        return  # "Please don't impersonate others."
    else:
        db.execute("insert or replace into karma(chan, word, karma)"
                   "values(?,?,?)", (chan, word.lower(), karma))
        db.commit()
        print ">>> u'Karma of %s set to %s :%s'" % (word, karma, chan)


@hook.command(autohelp=False)
def topkarma(inp, chan='', say=None, db=None):
    ".topkarma - returns 3 top karma'd items"
    db_init(db)
    items = db.execute(
        "select word, karma from karma where chan=? order by karma desc limit 3",
        (chan,)).fetchall()
    message = "Top karma'd items: "
    for item in items:
        message = message + item[0] + " with " + str(item[1]) + ", "
    say(message[:-2])


@hook.command(autohelp=False)
def botkarma(inp, chan='', say=None, db=None):
    ".botkarma - returns 3 lowest karma'd items"
    db_init(db)
    items = db.execute(
        "select word, karma from karma where chan=? order by karma limit 3",
        (chan,)).fetchall()
    message = "Lowest karma'd items: "
    for item in items:
        message = message + item[0] + " with " + str(item[1]) + ", "
    say(message[:-2])
