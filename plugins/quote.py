'''
quote.py - rewritten by MikeFightsBears 2013
'''

import random
import re
import time

from util import hook


def db_init(db):
    db.execute("create table if not exists quote"
               "(key INTEGER PRIMARY KEY, chan, nick, add_nick, msg, time real)")
    db.commit()


def add_quote(db, chan, nick, add_nick, msg):
    db.execute(
        '''insert into quote (chan, nick, add_nick, msg, time) values(?,?,?,?,?)''',
        (chan, nick, add_nick, msg, time.time()))
    db.commit()


def del_quote(key):
    db.execute('''delete from quote where key=?''',
               (key,))
    db.commit()


def get_quotes_by_nick(db, chan, nick):
    return db.execute(
        "select key, time, nick, msg from quote where chan=? and lower(nick)=lower(?) order by time",
        (chan, nick)).fetchall()


def get_quotes_by_chan(db, chan):
    return db.execute(
        "select key, time, nick, msg from quote where chan=? order by time",
        (chan,)).fetchall()


def get_quote_by_key(db, key):
    return db.execute("select key, time, nick, msg from quote where key=?",
                      (key,)).fetchall()


def format_quote(q):
    key, ctime, nick, msg = q
    return "Quote #%d: <%s> \"%s\" on %s" % (key, nick, msg,
                                             time.strftime("%Y-%m-%d", time.gmtime(ctime)))


@hook.command(autohelp=False)
def randomquote(inp, nick='', chan='', db=None, input=None):
    ".randomquote [nick] - gets random quote by <nick> or from the current channel"
    db_init(db)
    if inp == "":
        quotes = get_quotes_by_chan(db, chan)
    else:
        quotes = get_quotes_by_nick(db, chan, inp.strip(' '))

    n_quotes = len(quotes)

    if not n_quotes:
        return "No quotes found"

    num = random.randint(1, n_quotes)
    selected_quote = quotes[num - 1]
    return format_quote(selected_quote)


@hook.command
def getquote(inp, nick='', chan='', db=None):
    ".getquote <#n> - gets <#n>th quote by [nick] or from channel if no nick specified"
    db_init(db)
    if inp.strip().isdigit():
        num = int(inp.strip())
        quote = get_quote_by_key(db, num)
    else:
        return "Non integer input!"
    if quote:
        return format_quote(quote[0])
    else:
        return "That doesn't seem to exist"


@hook.command
def quote(inp, nick='', chan='', db=None):
    ".quote <nick> <msg> - gets adds quote"
    db_init(db)
    quoted_nick = inp.split(' ', 1)[0].strip('<> ')
    msg = inp.split(' ', 1)[1].strip(' ')

    try:
        add_quote(db, chan, quoted_nick, nick, msg)
        db.commit()
    except db.IntegrityError:
        return "Error in adding quote."
    return "Quote added."
