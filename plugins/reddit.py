from util import hook, http, text, timesince
from datetime import datetime
import re
import random

base_url = "http://reddit.com/r/{}/.json"
short_url = "http://redd.it/{}"


@hook.command
def reddit(inp):
    """.reddit <subreddit> [n] - Gets a random post from <subreddit>, or gets the [n]th post in the subreddit."""

    # clean and split the input
    parts = inp.lower().strip().split()
    id_num = None

    # find the requested post number (if any)
    if len(parts) > 1:
        inp = parts[0]
        try:
            id_num = int(parts[1]) - 1
        except ValueError:
            return "Invalid post number."

    try:
        data = http.get_json(base_url.format(inp.strip()))
    except Exception as e:
        return "Error: " + str(e)
    data = data["data"]["children"]

    # get the requested/random post
    if id_num is not None:
        try:
            item = data[id_num]["data"]
        except IndexError:
            length = len(data)
            return (
                "Invalid post number. Number must be between 1 and {}.".format(
                    length)
            )
    else:
        item = random.choice(data)["data"]

    item["title"] = text.truncate_str(item["title"], 50)
    item["link"] = short_url.format(item["id"])

    rawtime = datetime.fromtimestamp(int(item["created_utc"]))
    item["timesince"] = timesince.timesince(rawtime)

    if item["over_18"]:
        item["warning"] = " \x02NSFW\x02"
    else:
        item["warning"] = ""

    return u'\x02{title}\x02 - posted by \x02{author}\x02' \
        ' {timesince} ago - {ups} upvotes, {downs} downvotes -' \
        ' {link}{warning}'.format(**item)
