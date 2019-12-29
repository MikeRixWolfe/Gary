import re
from util import hook


def db_init(db):
    db.execute("create table if not exists karma(chan, word, karma,"
        " primary key(chan, word))")
    db.commit()


def get_karma(db, chan, word):
    row = db.execute("select karma from karma where chan=? and word=lower(?)",
        (chan, word)).fetchone()
    return row[0] if row else 0


def set_karma(db, chan, word, karma):
    try:
        db.execute("insert or replace into karma(chan, word, karma)"
            "values(?,?,?)", (chan, word.lower(), karma))
    except:
        pass
    db.commit()


@hook.regex(r'(\(.*\)|\S+)(\+\+|--)')
def karma_edit(inp, chan='', nick='', say=None, db=None):
    db_init(db)

    word, delta = inp.groups()
    if re.match(r'\(.*\)', word):
        word = word[1:-1]
    word = word.strip().lower()

    if word == nick.lower():
        return #"Please do not karma yourself."

    karma = int(get_karma(db, chan, word))
    if delta == "++":
        karma += 1
    elif delta == "--":
        karma -= 1
    set_karma(db, chan, word, karma)


@hook.command
def karma(inp, chan='', say=None, db=None, input=None):
    """karma <word> - Returns karma of <word>; <word>(++|--) increments or decrements karma of <word>."""
    db_init(db)

    if re.match(r'\(.*\)', inp):
        inp = inp[1:-1]
    word = inp.strip().lower()

    karma = get_karma(db, chan, word)

    if karma and karma != '0':
        say("%s has %s karma" % (word, karma))
    else:
        say("%s has neutral karma" % word)


@hook.command(adminonly=True)
def setkarma(inp, chan='', db=None):
    """setkarma <word> <value> - Sets karma value."""
    db_init(db)

    try:
        word, karma = inp.rsplit(' ',1)
    except:
        return setkarma.__doc__

    set_karma(db, chan, word, karma)
    return "Karma of %s set to %s" % (word, karma)

