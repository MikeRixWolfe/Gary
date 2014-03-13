'''
test.py - written by MikeFightsBears 2013
'''

from util import hook


@hook.command(autohelp=False)
def test(inp, nick='', say=None):
    ".test - tests your hilight window"
    say("Hello %s" % nick)


@hook.command(autohelp=False)
def kitchensink(inp, nick='', say=None):
    return "This function is still in development."


@hook.regex(r'^bot roll call')
def rollcall(inp, chan='', say=None):
    say("Ehh shut up ya dirty shisno")
