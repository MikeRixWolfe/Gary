from util import hook, http


@hook.command
def lmgtfy(inp, say=''):
    """.lmgtfy [phrase] - Posts a Google link for the specified phrase."""
    say("http://lmgtfy.com/?q={}".format(http.quote_plus(inp)))
