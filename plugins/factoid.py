import re
import datetime
from util import hook


def db_init(db):
    db.execute("create table if not exists factoids(chan, word, data, set_by, set_time,"
               " primary key(chan, word))")
    db.commit()


def get_factoid(db, chan, word):
    row = db.execute("select data from factoids where chan=? and word=lower(?)",
        (chan.lower(), word.lower())).fetchone()
    return (row[0] if row else None)


@hook.regex(r'^(no )?Gary(?::|, )([^\(].+?[^\)]|\(.+\)) is (also )?(.+)', re.I)
def set_factoid(inp, nick='', chan='', say=None, db=None):
    db_init(db)

    replace = inp.group(1)
    head = inp.group(2).strip('() ')
    append = inp.group(3)
    tail = inp.group(4).strip()

    data = get_factoid(db, chan, head)

    if data:
        if replace == "no ":
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
        db.execute("insert into factoids(chan, word, data, set_by, set_time) values"
                   " (lower(?),lower(?),?,lower(?),lower(?))", (chan, head, tail, nick, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        db.commit()
        say("Ok %s." % nick)


@hook.command
def forget(inp, chan='', say=None, db=None):
    """forget <word|phrase> - Forgets factoid."""
    db_init(db)
    word = inp.strip()
    data = get_factoid(db, chan, word)
    if data:
        db.execute("delete from factoids where chan=? and word=lower(?)",
                   (chan, word))
        db.commit()
        say("I forgot %s" % word)
    else:
        say("But... It doesn't exist!")


@hook.command
@hook.regex(r'^(.+)\?$')
def factoid(inp, chan='', say=None, db=None):
    "Gary: <word|(multi word)> is <data> - Sets <word|(multi word)> to <data>; " \
    "no Gary, <word|(multi word)> is <new data> - Resets <word|(multi word)> to <new data>; " \
    "Gary: <word|(multi word)> is also <additional data> - Adds <additional data> to <word|(multi word)>."
    db_init(db)
    word = inp.group(1).strip()
    data = get_factoid(db, chan, word)
    if data:
        say("%s is %s" % (word, data))
