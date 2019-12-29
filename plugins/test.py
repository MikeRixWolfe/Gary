from util import hook


@hook.command(autohelp=False)
def test(inp, nick='', say=None):
    """test - Tests your hilight window."""
    say("Hello %s" % nick + ('; "%s"' % inp if inp else ""))

