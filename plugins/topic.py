import json
from util import hook


def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


@hook.command
def topic(inp, chan=None, conn=None, bot=None):
    """.topic <add|del> <topic> - Change the topic of a channel."""
    split = inp.split(" ", 1)

    if chan.startswith('#') and len(split) == 2:
        t = bot.config['topics'].get(chan, None)

        if split[0] == 'add':
            if t == '':
                bot.config['topics'][chan] = split[1]
            else:
                t = t.split(' | ')
                t.insert(0, split[1])
                bot.config['topics'][chan] = ' | '.join(t)

            json.dump(bot.config, open('config', 'w'), sort_keys=True, indent=2)
            conn.send("TOPIC {} :{}".format(chan, bot.config['topics'][chan]))
        elif split[0] == 'del' and is_int(split[1]):
            try:
                t = t.split(' | ')
                t.pop(int(split[1]))
                bot.config['topics'][chan] = ' | '.join(t)

                json.dump(bot.config, open('config', 'w'), sort_keys=True, indent=2)
                conn.send("TOPIC {} :{}".format(chan, bot.config['topics'][chan]))
            except:
                pass
        else:
            return "Check your input and try again."

