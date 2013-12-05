from util import hook

@hook.command(autohelp=False)
def test(inp, nick='', say=None):
    ".test - tests your hilight window"
    say("Hello %s" % nick)
