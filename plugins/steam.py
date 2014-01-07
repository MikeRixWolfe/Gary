import re
from util import hook, http, web, text
from bs4 import BeautifulSoup


def get_steam_info(url):
    # we get the soup manually because the steam pages have some odd encoding troubles
    page = http.get(url)
    soup = BeautifulSoup(page, 'lxml', from_encoding="utf-8")

    name = soup.find('div', {'class': 'apphub_AppName'}).text
    desc = ": " + text.truncate_str(soup.find('div', {'class': 'game_description_snippet'}).text.strip())

    # the page has a ton of returns and tabs
    details = soup.find('div', {'class': 'glance_details'}).text.strip().split(u"\n\n\r\n\t\t\t\t\t\t\t\t\t")
    genre = " - Genre: " + details[0].replace(u"Genre: ", u"")
    date = " - Release date: " + details[1].replace(u"Release Date: ", u"")
    price = ""
    if not "Free to Play" in genre:
        price = " - Price: " + soup.find('div', {'class': 'game_purchase_price price'}).text.strip()

    return name + desc + genre + date + price


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
