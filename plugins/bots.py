"""
bots.py: written by MikeFightsBears.com
"""

import json
from util import hook


@hook.sieve
def m2_sieve(bot, input, func, kind, args):
    # don't block input to event hooks
    if kind == "command":
        if input.msg == 'Gary: no idea' and input.nick == 'M2':
            return None
        if input.trigger == "help" and input.chan[0] == '#' and input.nick == "timmaha":
            return None
    return input


