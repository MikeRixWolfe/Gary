import time
from util import hook, timesince, text


def db_init(db):
    "check to see that our db has the tell table and return a dbection."
    db.execute("create table if not exists tell"
               "(user_to, user_from, message, chan, time,"
               "primary key(user_to, message))")
    db.commit()

    return db


def get_tells(db, user_to, chan):
    return db.execute("select user_from, message, time from tell where"
                      " user_to=lower(?) and chan=lower(?) order by time",
                      (user_to.lower(), chan)).fetchall()


@hook.event('*')
def showtells(inp, say='', nick='', chan='', db=None):
    db_init(db)
    tells = get_tells(db, nick, chan)

    if not tells:
        return
    for tell in tells:
        user_from, message, time = tell
        past = timesince.timesince(time)
        say("%s: Message from %s, %s ago: %s" %
            (nick, user_from, past, message))  # notice(

    db.execute("delete from tell where user_to=lower(?) and chan=lower(?)",
               (nick, chan))
    db.commit()


@hook.command('rmsg')
@hook.command('msg')
@hook.command
def message(inp, nick='', chan='', conn=None, db=None, input=None, bot=None):
    """.msg/.message <nick> <message> - Relay <message> to <nick> when <nick> is around."""

    query = inp.split(' ', 1)

    if len(query) != 2:
        return tell.__doc__

    user_to = query[0].lower()
    message = query[1].strip()
    user_from = nick

    #if user_to in conn.users.keys():
    #    return "%s is currently online, please use /msg instead." % user_to

    if user_to in bot.config['ignored']:
        return "I've been instructed not to interact with %s." % user_to

    if input.trigger == 'rmsg':
        message = text.rainbow(message)

    if chan.lower() == user_from.lower():
        chan = 'a pm'

    if user_to == user_from.lower():
        return "Have you looked in a mirror lately?"

    if input.conn.nick.lower() == user_to.lower():
        # user is looking for us, being a smartass
        return "You need to get your eyes checked."

    db_init(db)

    if db.execute("select count() from tell where user_to=?",
                  (user_to,)).fetchone()[0] >= 5:
        return "That person has too many things queued."

    try:
        db.execute("insert into tell(user_to, user_from, message, chan,"
                   "time) values(?,?,?,?,?)", (user_to, user_from, message,
                                               chan, time.time()))
        db.commit()
    except db.IntegrityError:
        return "Message has already been queued."

    return "I'll pass that along."
