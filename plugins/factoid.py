"""
factoid.py: written by MikeFightsBears 2013
"""

import datetime
from util import hook


def db_init(db):
    db.execute("create table if not exists factoids(chan, word, data, set_by, set_time,"
        	" primary key(chan, word))")
    db.commit()


def get_factoid(db, chan, word):
    row = db.execute("select data from factoids where chan=? and word=lower(?)",
		(chan.lower(), word.lower())).fetchone()
    if row:
        return row[0]
    else:
        return None

#@hook.regex(r'^(no\ )?(?:G|g)ary(?:\:\ |\,\ |\ )([^\.][\S]+|.*)\ (?:is)\ (also\ )?\<reply\>(.+)') #m2 style

@hook.singlethread
@hook.regex(r'^(no\ )?(?:G|g)ary(?:\:\ |\,\ |\ )([^\(].*?[^\)]|\(.*\))\ (?:is)\ (also\ )?(.+)') #Geekboy Style
def set_factoid(inp, nick='', chan='', say=None, db=None):
    #Backup documentation for m2 style factoids
    "Gary: [word|phrase] is <reply> [data] - sets [word|phrase] to [data]; \
    no Gary, [word|phrase] is <reply> [new data] - resets [word|phrase] to [new data]; \
    Gary: [word|phrase] is also <reply> [additional data] - adds [additional data] to [word]"
    db_init(db)

    replace=inp.group(1)
    head=inp.group(2).strip('() ')
    append=inp.group(3)
    tail=inp.group(4).strip()

    data = get_factoid(db, chan, head)

    if data:
        if replace == "no ":
            if append == "also ":
                tail = append + tail
            db.execute("replace into factoids(chan, word, data, set_by, set_time) values"
                " (lower(?),lower(?),?,lower(?),lower(?))", (chan, head, tail, nick, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            db.commit()
            return 'Ok %s.' % nick
        elif append == "also " and replace != "no ": 
            tail = data + " or " + tail
            db.execute("replace into factoids(chan, word, data, set_by, set_time) values"
                " (lower(?),lower(?),?,lower(?),lower(?))", (chan, head, tail, nick, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            db.commit()
            return 'Ok %s.' % nick
        else:
            return 'but, "%s" is "%s"...' % (head, data)
    else:
        if append == "also ":
            tail = append + tail
        db.execute("insert into factoids(chan, word, data, set_by, set_time) values"
            " (lower(?),lower(?),?,lower(?),lower(?))", (chan, head, tail, nick, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        db.commit()
        say("Ok %s." % nick)


@hook.command
def forget(inp, chan='', say=None, db=None):
    ".forget <word|phrase> - forgets factoid"
    db_init(db)
    word=inp.strip()
    data = get_factoid(db, chan, word)
    #if not chan.startswith('#'):
    #    return "I won't forget anything in private."
    if data:
        db.execute("delete from factoids where chan=? and word=lower(?)",
                   (chan, word))
        db.commit()
        say("I forgot %s" % word)
    else:
        say("But... It doesn't exist!")


@hook.command
@hook.regex(r'^(.+)\?')
def factoid(inp, chan='', say=None, db=None):
    "Gary: <word|(multi word)> is <data> - sets <word|(multi word)> to <data>; \
    no Gary, <word|(multi word)> is <new data> - resets <word|(multi word)> to <new data>; \
    Gary: <word|(multi word)> is also <additional data> - adds <additional data> to <word|(multi word)>"
    db_init(db)
    word=inp.group(1).strip()
    data = get_factoid(db, chan, word)
    if data:
        say("%s is %s" % (word,data))
