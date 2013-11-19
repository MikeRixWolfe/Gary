"""
rollcall.py written by MikeFightsBears 2013
"""

from util import hook

@hook.regex(r'^bot roll call')
def rollcall(inp, chan='', say=None):
    say("Ah shut up ya dirty shisno")
