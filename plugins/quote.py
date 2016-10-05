import random
import re
import time
from util import hook


def db_init(db):
    db.execute("create table if not exists quote"
               "(key INTEGER PRIMARY KEY, chan, msg, nick, time real)")
    db.commit()


def add_quote(db, chan, msg, nick):
    db.execute("insert into quote (chan, msg, nick, time)" \
        " values(?,?,?,?)", (chan, msg, nick, time.time()))
    db.commit()


def del_quote(key):
    db.execute("delete from quote where key=?", (key,))
    db.commit()


def get_quote_by_chan(db, chan):
    return db.execute("select key, msg, nick, time from quote where" \
        " chan=? order by random() limit 1", (chan,)).fetchone()


def get_quote_by_key(db, key, chan):
    return db.execute("select key, msg, nick, time from quote where " \
        "key=? and chan=?", (key, chan)).fetchone()


def format_quote(q):
    key, msg, nick, ctime = q
    return 'Quote #{}: "{}" by {} at {}'.format(key, msg, nick,
        time.strftime("%H:%M on %m-%d-%Y", time.gmtime(ctime)))


@hook.command('rq', autohelp=False)
@hook.command(autohelp=False)
def randomquote(inp, nick='', chan='', db=None, input=None):
    """.randomquote - Gets a random quote by <nick> or from the current channel."""
    db_init(db)
    quote = get_quote_by_chan(db, chan)

    if quote:
        return format_quote(quote)
    else:
        return "No quotes found for this channel."


@hook.command
def getquote(inp, nick='', chan='', db=None):
    """.getquote <n> - Gets the <n>th quote."""
    db_init(db)

    try:
        quote = get_quote_by_key(db, inp, chan)
        return format_quote(quote)
    except:
        return "That doesn't seem to exist."


@hook.command
def quote(inp, nick='', chan='', db=None):
    """.quote <msg> - Adds quote."""
    db_init(db)

    if inp:
        try:
            add_quote(db, chan, inp, nick)
        except db.IntegrityError:
            return "Error in adding quote."
        return "Quote added."
    else:
        return "Check your input and try again."

