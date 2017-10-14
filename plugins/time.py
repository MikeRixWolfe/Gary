import time
from util import hook, http, text

api_url = 'http://api.wolframalpha.com/v2/query?format=plaintext'


@hook.command("time")
def time_command(inp, say=None, bot=None):
    """.time <area> - Gets the time in <area>."""
    query = "current time in {}".format(inp)

    api_key = bot.config.get("api_keys", {}).get("wolframalpha", None)
    if not api_key:
        return "Error: No Wolfram Alpha API key set."

    try:
        request = http.get_xml(api_url, input=query, appid=api_key)
    except:
        return "Error parsing data from Wolfram Alpha; please try again in a few minutes."

    time = " ".join(request.xpath("//pod[@title='Result']/subpod/plaintext/text()"))
    time = time.replace("  |  ", ", ")

    if time:
        # nice place name for UNIX time
        if inp.lower() == "unix":
            place = "Unix Epoch"
        else:
            place = text.capitalize_first(" ".join(request.xpath("//pod[@" \
                "title='Input interpretation']/subpod/plaintext/text()")).split('|')[0])
            place = place.replace("Current Time In", "").strip()
        say(u"\x02{}\x02 - {}".format(place, time))
    else:
        return "Could not get the time for '{}'.".format(inp)


