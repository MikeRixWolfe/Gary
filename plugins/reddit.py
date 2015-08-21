import re
import random
from util import hook, http, text, timesince, web
from datetime import datetime

base_url = "http://reddit.com/r/{}/.json"
short_url = "http://redd.it/{}"
reddit_re = (r'.*((www\.)?reddit\.com/r[^ ]+)', re.I)


@hook.regex(*reddit_re)
def reddit_url(match, say=None):
    thread = http.get_html(match.group(0))

    title = thread.xpath('//title/text()')[0]
    try:
        upvotes = thread.xpath(
            "//div[@class='score']/span[@class='number']/text()")[0]
        author = thread.xpath(
            "//div[@id='siteTable']//a[contains(@class,'author')]/text()")[0]
        timeago = thread.xpath(
            "//div[@id='siteTable']//p[@class='tagline']/time/text()")[0]
        comments = thread.xpath(
            "//li[@class='first']/a[@class='comments may-blank']/text()")[0]

        say(u'{} - \x02{}\x02 - posted by \x02{}\x02 {} ago - {} upvotes - {}'.format(
            web.try_googl(match.group(0)), title, author, timeago, upvotes, comments))
    except:  # Subreddit
        say(u'{} - \x02{}\x02'.format(web.try_googl(match.group(0)), title))


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

    item["title"] = text.truncate_str(item["title"], 100)
    item["link"] = short_url.format(item["id"])

    rawtime = datetime.fromtimestamp(int(item["created_utc"]))
    item["timesince"] = timesince.timesince(rawtime)

    if item["over_18"]:
        item["warning"] = " \x02NSFW\x02"
    else:
        item["warning"] = ""

    return u'{link}{warning} - \x02{title}\x02 - posted by' \
        ' \x02{author}\x02 {timesince} ago - {ups} upvotes,' \
        ' {downs} downvotes'.format(**item)


@hook.command
def ris(inp):
    """.ris <subreddit> - Reddit image search for random imgur link from subreddit."""
    inp = inp.split(' ')[0]
    try:
        data = http.get_json("http://reddit.com/r/%s/.json" % inp)
    except Exception as e:
        return "Error: " + str(e)
    data = data["data"]["children"]
    item = None
    random.shuffle(data)
    for tempitem in data:
        if tempitem["data"]["domain"] == "i.imgur.com":
            item = tempitem["data"]
        if item:
            return u"{} - \x02{}\x02".format(item['url'], item['title'])
    return "No image posts found for \x02r/{}\x02".format(inp)
