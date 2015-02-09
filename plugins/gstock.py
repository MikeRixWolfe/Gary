import json
from util import hook, http, web


@hook.command
def gstock(inp):
    """.gstock <symbol> - Gets stock information from Google."""
    # Note: NASDAQ:GOOG,NASDAQ:YHOO is a valid example input
    try:
        quote = json.loads(http.get("http://finance.google.com/finance/info",
            client="ig", format="json", q=inp)[3:])[0]
    except:
        return "Google Finance API error, please try again in a few minutes."

    quote["color"] = "5" if quote["c"][0] == "-" else "3"
    quote["chart"] = web.try_googl("http://www.google.com/finance/chart?tlf=12&q=" + inp)

    return "{t}: ${l} \x03{color}{c} ({cp}%)\x03 - {chart} [{ltt}]".format(**quote)

