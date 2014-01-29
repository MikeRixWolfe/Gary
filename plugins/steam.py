import re
import json
from util import hook, http, web, text
from bs4 import BeautifulSoup


def get_steam_info(url):
    appid = re.match(r'.*?/app/(.+)/', url).group(1)
    appdata = http.get_json(
        "http://store.steampowered.com/api/appdetails/?appids={}".format(appid))
    print appid
    name = appdata[appid]["data"]["name"].encode("ascii", "ignore")
    #desc = text.truncate_str(re.sub('<[^<]+?>', '', appdata[appid]["data"]["about_the_game"]))
    genres = []
    for genre in appdata[appid]["data"]["genres"]:
        genres.append(genre["description"])
    date = appdata[appid]["data"]["release_date"]["date"]
    if not "Free to Play" in genres:
        raw_price = str(appdata[appid]["data"]["price_overview"]["final"])
        price = "$" + raw_price[:-2] + "." + raw_price[-2:]
    else:
        price = "Free to Play"
        genres.remove("Free to Play")
    genre = "/".join(genres)

    # return "\x02{}\x0F: {} - {} - {} - {}".format(name, desc, genre, date,
    # price)
    return "\x02{}\x0F: {} - {} - {}".format(name, genre, date, price)


@hook.command
def steam(inp):
    """steam [search] - Search for specified game/trailer/DLC"""
    page = http.get("http://store.steampowered.com/search/?term=" + inp)
    soup = BeautifulSoup(page, 'lxml', from_encoding="utf-8")
    result = soup.find('a', {'class': 'search_result_row'})
    try:
        return get_steam_info(result['href']) + " - " + web.isgd(result['href'])
    except Exception as e:
        print "Steam search error: {}".format(e)
        return "Steam API error, please try again later."
