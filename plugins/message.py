import time
from util import hook, text, timesince


def db_init(db):
    "check to see that our db has the tell table and return a db."
    db.execute("create table if not exists tell"
               "(user_to, user_from, message, chan, time,"
               "primary key(user_to, message))")
    db.commit()

    return db


def get_tells(db, recip, chan):
    return db.execute("select user_from, message, chan, time from tell where"
                      " user_to=lower(?) and (chan=lower(?) or"
                      " chan not like '#%') order by time",
                      (recip.lower(), chan)).fetchall()


@hook.event('PRIVMSG')
def showtells(paraml, say='', nick='', chan='', conn=None, db=None):
    db_init(db)
    tells = get_tells(db, nick, chan)

    if tells:
        for tell in tells:
            if '#' in tell[2]:
                say("{nick}: Message from {}, {time} ago: {}".format(nick=nick,
                    time=timesince.timesince(tell[-1]), *tell))
            else:
                out = "PM from {}, {time} ago: {}".format(
                    time=timesince.timesince(tell[-1]), *tell)
                conn.send("PRIVMSG {} :{}".format(nick, out))
        db.execute("delete from tell where user_to=lower(?) and (chan=lower(?)"
                   " or chan not like '#%')",(nick, chan))
        db.commit()


@hook.command('rmsg')
@hook.command('msg')
@hook.command
def message(inp, nick='', chan='', conn=None, db=None, input=None, bot=None):
    """.msg/.message <nick> <message> - Relay <message> to <nick> when <nick> is around."""
    try:
        recip, msg = inp.lower().split(' ', 1)
    except:
        return message.__doc__

    if recip in conn.users.keys():
        return "{} is currently online, please use /msg instead.".format(recip)
    if recip in bot.config['ignored']:
        return "I've been instructed not to interact with {}.".format(recip)
    if recip == nick.lower():
        return "Have you looked in a mirror lately?"
    if recip == input.conn.nick.lower():
        return "You need to get your eyes checked."

    if input.trigger == 'rmsg':
        msg = text.rainbow(msg)

    db_init(db)

    if len(get_tells(db, recip, chan)) >= 5:
        return "{} has too many messages queued.".format(recip)

    try:
        db.execute("insert into tell(user_to, user_from, message, chan,"
                   "time) values(?,?,?,?,?)", (recip, nick, msg,
                                               chan, time.time()))
        db.commit()
    except db.IntegrityError:
        return "Message has already been queued."

    return "I'll pass that along."
