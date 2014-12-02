from util import hook


@hook.command(autohelp=False)
def test(inp, nick='', say=None):
    """.test - Tests your hilight window."""
    say("Hello %s" % nick + ('; "%s"' % inp if inp else ""))


@hook.command(autohelp=False)
def kitchensink(inp, nick='', say=None):
    return "This function is still in development."


@hook.regex(r'^bot roll call')
def rollcall(inp, chan='', say=None):
    say("Knock knock, Church")
