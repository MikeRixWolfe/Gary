import time
from util import hook, text


def db_init(db):
    db.execute("create table if not exists quotes"
               "(id INTEGER PRIMARY KEY, quote TEXT, nick TEXT, active INTEGER, uts REAL)")
    db.commit()


def add_quote(db, quote, nick):
    db.execute("insert into quotes (quote, nick, active, uts)" \
        " values(?,?,?,?)", (quote, nick, 1, time.time()))
    db.commit()


def del_quote(db, id):
    update = db.execute("update quotes set active=0 where id=? and active=1", (id,))
    db.commit()
    return update


def restore_quote(db, id):
    update = db.execute("update quotes set active=1 where id=? and active=0", (id,))
    db.commit()
    return update


def search_quote(db, text):
    text = '%{}%'.format(text)
    ids = db.execute("select id from quotes where quote like ? and active=1", (text,)).fetchall()
    return ids


def get_random_quote(db):
    return db.execute("select id, quote, nick, uts from quotes" \
        " where active=1 order by random() limit 1").fetchone()


def get_random_quote_with_text(db, text):
    text = '%{}%'.format(text)
    return db.execute("select id, quote, nick, uts from quotes" \
        " where active=1 and quote like ? order by random() limit 1", (text,)).fetchone()


def get_quote_by_id(db, id):
    return db.execute("select id, quote, nick, uts from quotes where" \
        " id=? and active=1", (id,)).fetchone()


def format_quote(q):
    id, quote, nick, uts = q
    return 'Quote #{}: "{}" set by {} in {}'.format(id, quote, nick,
        time.strftime("%B %Y", time.localtime(uts)))


@hook.command('rq', autohelp=False)
@hook.command(autohelp=False)
def randomquote(inp, say=None, db=None, input=None):
    """randomquote - Gets a random quote."""
    db_init(db)

    if inp:
        quote = get_random_quote_with_text(db, inp)
    else:
        quote = get_random_quote(db)

    if quote:
        say(format_quote(quote))
    else:
        return "No quotes found."


@hook.command
def getquote(inp, say=None, db=None):
    """getquote <n> - Gets the <n>th quote."""
    db_init(db)
    quote = get_quote_by_id(db, inp)

    if quote:
        say(format_quote(quote))
    else:
        return "Quote #{} was not found.".format(inp)


@hook.command
def searchquote(inp, say=None, db=None):
    """searchquote <text> - Returns IDs for quotes matching <text>."""
    db_init(db)
    ids = search_quote(db, inp)

    if quote:
        say(text.truncate_str("Quotes: {}".format(
            ', '.join([str(id[0]) for id in ids])), 350))
    else:
        return "None found."


@hook.command
def delquote(inp, chan='', db=None):
    """delquote <n> - Deletes the <n>th quote."""
    db_init(db)
    quote = del_quote(db, inp)

    if quote.rowcount > 0:
        return "Quote #{} deleted.".format(inp)
    else:
        return "Quote #{} was not found.".format(inp)


@hook.command
def restorequote(inp, chan='', db=None):
    """restorequote <n> - Restores the <n>th quote."""
    db_init(db)
    quote = restore_quote(db, inp)

    if quote.rowcount > 0:
        return "Quote #{} restored.".format(inp)
    else:
        return "Quote #{} was not found.".format(inp)


@hook.command
def quote(inp, nick='', chan='', say=None, db=None):
    """quote <msg> - Adds a quote."""
    db_init(db)

    if inp:
        try:
            add_quote(db, inp, nick)
        except db.IntegrityError:
            return "Error in adding quote."
        say("Quote added.")
    else:
        return "Check your input and try again."

