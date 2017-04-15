import time
from util import hook

joins = []
timeouts = {}
join_limit_lockdown_active = False
chat_limit_lockdown_active = False
join_limit_chans = ['#geekperson']
chat_limit_chans = ['#geekperson']


@hook.event('*')
def security_tracking(paraml, bot=None, chan=None, conn=None, input=None, nick=None, say=None):
    if input.command == 'JOIN' and chan in join_limit_chans:
        global joins, join_limit_lockdown_active
        join_limit = 3
        join_limit_threshold = 10
        join_limit_timeout = 300

        joins.append(int(time.time()))
        joins = [j for j in joins if time.time() - j < join_limit_threshold]

        if len(joins) >= join_limit and not join_limit_lockdown_active \
                and bot.start_time > 600:
            conn.send("MODE {} +i".format(chan))
            join_limit_lockdown_active = True
            say("There have been an abnormally large number of joins in the " \
                "past few seconds, as such I have set the channel mode to " \
                "invite only. I will autmatically revert this in {} " \
                "seconds.".format(join_limit_timeout))

            time.sleep(join_limit_timeout)

            conn.send("MODE {} -i".format(chan))
            join_limit_lockdown_active = False

    if input.command == 'PRIVMSG' and chan in chat_limit_chans:
        global timeouts, chat_limit_lockdown_active
        chat_limit = 10
        chat_limit_threshold = 15
        chat_limit_timeout = 300

        if timeouts.get(nick, None) is None:
            timeouts[nick] = {}
            timeouts[nick]['msgs'] = [time.time()]
        else:
            timeouts[nick]['msgs'].append(time.time())
            timeouts[nick]['msgs'] = [msg for msg in
                timeouts[nick]['msgs'] if time.time() - msg < chat_limit_threshold]

        if len(timeouts[nick]['msgs']) >= chat_limit and not chat_limit_lockdown_active \
                and bot.start_time > 600:
            conn.send("MODE {} +i".format(chan))
            conn.send("KICK {} {} :{}".format(chan, nick, "Automated kick - No spamming please."))
            chat_limit_lockdown_active = True
            say("There have been an abnormally large number of lines in the " \
                "past few seconds, as such I have set the channel mode to " \
                "invite only. I will autmatically revert this in {} " \
                "seconds.".format(chat_limit_timeout))

            time.sleep(chat_limit_timeout)

            conn.send("MODE {} -i".format(chan))
            chat_limit_lockdown_active = False

