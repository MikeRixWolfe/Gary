from util import hook

@hook.command('test', autohelp=False)
@hook.command(autohelp=False)
def hello(inp, nick='', say=None):
    ".test - tests your hilight window"
    say("Hello %s" % nick)
