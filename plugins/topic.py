import json
import re
from util import hook


@hook.event('TOPIC')
def ontopic(paraml, nick='', chan=None, conn=None, bot=None):
    if nick != conn.nick:
        bot.config['topics'][chan] = paraml[-1]
        json.dump(bot.config, open('config', 'w'), sort_keys=True, indent=2)
        print(">>> u'Manual topic update: '{}' :{}'".format(paraml[-1], chan))


@hook.command
def topic(inp, chan=None, conn=None, bot=None):
    """topic <add|app|del #|set #|ins #> <topic> - Change the topic of a channel. For deletion this may be a #-# range. This is zero indexed."""
    if chan.startswith('#') and len(inp.split()) > 1:
        _topic = [t for t in bot.config['topics'].get(chan, u'').split(u' | ') if t]
        op, idx0, idx1, clause = re.match(r'^(\S+)(?: (\d)-?(\d)?)?(?: (.*))?$', inp).groups()

        if op == 'add' and clause:
            if len(_topic) == 0:
                _topic = [clause]
            else:
                _topic.insert(0, clause)
        elif op in ['app', 'append'] and clause:
            if len(_topic) == 0:
                _topic = [clause]
            else:
                _topic.append(clause)
        elif op == 'set' and idx0 and clause:
            _topic[int(idx0)] = clause
        elif op in ['ins', 'insert'] and idx0 and clause:
            _topic.insert(int(idx0), clause)
        elif op in ['del', 'delete'] and int(idx0) <= int(idx1 or idx0) and int(idx1 or idx0) < len(_topic):
            for i in range(int(idx0), int(idx1 or idx0) + 1):
                _topic.pop(int(idx0))
        else:
            return "Check your input and try again."

        bot.config['topics'][chan] = u' | '.join(_topic)
        json.dump(bot.config, open('config', 'w'), sort_keys=True, indent=2)
        conn.send(u"TOPIC {} :{}".format(chan, bot.config['topics'][chan]))

