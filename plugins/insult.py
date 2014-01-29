"insult.py - MikeFightsBears 2013"

from random import choice
from util import hook

noun = ["ass", "back", "cock", "dick", "shit", "team"]
adjective = ["eating", "fucking", "killing", "stabbing", "sucking"]
prefix = ["blowjob", "cock", "dick", "dip", "douche", "fuck"]
suffix = ["bag", "berry", "biscuit", "bite", "shit", "tard", "whore"]


@hook.command
def insult(inp, say=''):
    ".insult <user> - Insults specified user with string built with insults from Red vs Blue"
    say("%s: You %s-%s %s%s" %
        (inp.strip(), choice(noun), choice(adjective), choice(prefix), choice(suffix)))
