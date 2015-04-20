"""
Adapted from CloudBotIRC/CloudBot
"""

import re
from util import hook, http, text, web


steam_re = (r'(.*:)//(store.steampowered.com)(:[0-9]+)?(.*)', re.I)

API_URL = "http://store.steampowered.com/api/appdetails/"
STORE_URL = "http://store.steampowered.com/app/{}/"


def format_data(app_id, show_url=True):
    """
    takes a steam appid and returns a formatted string with info
    :param appid: string
    :return: string
    """
    try:
        data = http.get_json(API_URL, appids=app_id)
    except Exception as e:
        return "Could not get game info: {}".format(e)

    game = data[app_id]["data"]
    out = []

    # basic info
    out.append(u"\x02{}\x02".format(game["name"]))
    desc = text.strip_html(game["about_the_game"])
    #out.append(text.truncate_str(desc, 70))

    # genres
    genres = ", ".join([g['description'] for g in game["genres"]])
    out.append("\x02{}\x02".format(genres))

    # release date
    if game['release_date']['coming_soon']:
        out.append("coming \x02{}\x02".format(game['release_date']['date']))
    else:
        out.append("released \x02{}\x02".format(game['release_date']['date']))

    # pricing
    if game['is_free']:
        out.append("\x02free\x02")
    else:
        price = game['price_overview']

        if price['final'] == price['initial']:
            out.append("\x02$%d.%02d\x02" % divmod(price['final'], 100))
        else:
            price_now = "$%d.%02d" % divmod(price['final'], 100)
            price_original = "$%d.%02d" % divmod(price['initial'], 100)

            out.append("\x02{}\x02 (was \x02{}\x02)".format(price_now, price_original))

    if show_url:
        url = web.try_googl(STORE_URL.format(game['steam_appid']))
        out.append(url)

    return " - ".join(out)


@hook.regex(*steam_re)
def steam_url(match):
    app_id = match.group(1)
    return format_data(app_id, show_url=False)


@hook.command()
def steam(text):
    """steam [search] - Search for specified game/trailer/DLC"""
    try:
        soup = http.get_soup("http://store.steampowered.com/search/", term=text.strip().lower())
    except Exception as e:
        return "Could not get game info: {}".format(e)
    result = soup.find('a', {'class': 'search_result_row'})

    if not result:
        return "No game found."

    app_id = result['data-ds-appid']
    return format_data(app_id)
