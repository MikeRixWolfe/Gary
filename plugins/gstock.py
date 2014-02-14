from util import hook, stock


@hook.command()
def gstock(inp, say=None):
    ".gstock <symbol> / .gstock <exchange>:<symbol> - Returns the current value of a given stock, default market is NASDAQ. Automatically searches for symbols given company names."
    say(stock.getstock(inp) or "Google Finance API error, please try again in a few minutes")
