from util import hook, http


@hook.command
def lmgtfy(inp):
    """.lmgtfy [phrase] - Posts a google link for the specified phrase"""
    link = "http://lmgtfy.com/?q={}".format(http.quote_plus(inp))
    return link
