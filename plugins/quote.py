import time
from util import hook, text, tokenize, web


def db_init(db):
    db.execute("create virtual table if not exists quotefts" \
        " using FTS5(id, msg, nick, active, uts)")
    db.commit()


def add_quote(db, quote, nick):
    id = db.execute("select max(cast(id as int)) from quotefts").fetchone()
    id = id[0] + 1 if id else 1
    db.execute("insert into quotefts (id, msg, nick, active, uts)" \
        " values(?,?,?,?,?)", (str(id), quote, nick, '1', str(time.time())))
    db.commit()
    return id


def del_quote(db, id):
    update = db.execute("update quotefts set active='0' where id=? and active='1'", (id,))
    db.commit()
    return update


def restore_quote(db, id):
    update = db.execute("update quotefts set active='1' where id=? and active='0'", (id,))
    db.commit()
    return update


def search_quote(db, text):
    ids = db.execute("select id from quotefts where quotefts match ?",
        ('{} AND active:"1"'.format(tokenize.build_query(text)),)).fetchall()
    return ids


def get_random_quote(db):
    return db.execute("select id, msg, nick, uts from quotefts" \
        " where active='1' order by random() limit 1").fetchone()


def get_random_quote_with_text(db, text):
    return db.execute("select id, msg, nick, uts from quotefts" \
        " where quotefts match ? order by random() limit 1",
        ('{} AND active:"1"'.format(tokenize.build_query(text)),)).fetchone()


def get_quote_by_id(db, id):
    return db.execute("select id, msg, nick, uts from quotefts where" \
        " id=? and active='1'", (id,)).fetchone()


def get_quote_timestamp(db, text):
    return db.execute("select time from logfts where msg match ?",
        ("quote" + text)).fetchone()


def get_log_link(bot, db, q):
    if bot.config.get("logviewer_url"):
        id, quote, nick, uts = q
        #match_clause = 'time:"{}"* AND msg:"{}"'.format(time.strftime("%Y-%m-%d", time.localtime(float(uts))), quote)
        match_clause = 'nick:"{}" AND msg:"quote {}"'.format(nick, quote)

        row = db.execute("select chan, time from logfts where logfts match ? order by cast(uts as decimal) asc",
            (match_clause, )).fetchone()

        try:
            chan, _datetime = row
            _date, _time = _datetime.split()
        except:
            print(match_clause)
            return '???'

        return web.try_googl(bot.config["logviewer_url"].format(chan.strip('#'), _date, _time))
    else:
        return ""


def format_quote(q, link):
    id, quote, nick, uts = q
    half = "Early" if time.strftime("%d", time.localtime(float(uts))) < 15 else "Late"

    return u'Quote #{}: "{}" set by {} ({} {}) {}'.format(id, quote, nick, half,
        time.strftime("%B %Y", time.localtime(float(uts))), link).strip()


@hook.command('rq', autohelp=False)
@hook.command('randquote', autohelp=False)
@hook.command(autohelp=False)
def randomquote(inp, bot=None, db=None, say=None):
    """randomquote - Gets a random quote."""
    db_init(db)

    if inp:
        quote = get_random_quote_with_text(db, inp)
    else:
        quote = get_random_quote(db)

    if quote:
        link = get_log_link(bot, db, quote)
        say(format_quote(quote, link))
    else:
        return "No quotes found."


@hook.command
def getquote(inp, bot=None, db=None, say=None):
    """getquote <n> - Gets the <n>th quote."""
    db_init(db)
    quote = get_quote_by_id(db, inp)

    if quote:
        link = get_log_link(bot, db, quote)
        say(format_quote(quote, link))
    else:
        return "Quote #{} was not found.".format(inp)


@hook.command
def searchquote(inp, say=None, db=None):
    """searchquote <text> - Returns IDs for quotes matching <text>."""
    db_init(db)
    ids = search_quote(db, inp)

    if ids:
        say(text.truncate_str("Quotes: {}".format(
            ', '.join([str(id[0]) for id in ids])), 350))
    else:
        return "None found."


@hook.command('deletequote')
@hook.command
def delquote(inp, db=None):
    """delquote <n> - Deletes the <n>th quote."""
    db_init(db)
    quote = del_quote(db, inp)

    if quote.rowcount > 0:
        return "Quote #{} deleted.".format(inp)
    else:
        return "Quote #{} was not found.".format(inp)


@hook.command
def restorequote(inp, db=None):
    """restorequote <n> - Restores the <n>th quote."""
    db_init(db)
    quote = restore_quote(db, inp)

    if quote.rowcount > 0:
        return "Quote #{} restored.".format(inp)
    else:
        return "Quote #{} was not found.".format(inp)


@hook.command
def quote(inp, nick='', say=None, db=None):
    """quote <msg> - Adds a quote."""
    db_init(db)

    if inp:
        try:
            id = add_quote(db, inp, nick)
        except db.IntegrityError:
            return "Error in adding quote."
        say("Quote #{} added.".format(id))
    else:
        return "Check your input and try again."

