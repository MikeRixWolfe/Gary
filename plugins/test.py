from util import hook

@hook.command(autohelp=False)
def test(inp, nick='', say=None):
    ".test - tests your hilight window"
    say("Hello %s" % nick)

@hook.command(autohelp=False)
def kitchensink(inp, nick='', say=None):
    return "This function is still in development."

@hook.command(autohelp=False)
def mulched(inp, nick='', say=None):
    say("Get mulched %s." % nick)

