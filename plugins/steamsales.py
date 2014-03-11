"""
steam_sales.py - Written by MikeRixWolfe 2013
"""

import time
import json
import os
from util import hook, http, web
from datetime import datetime

debug = False

def log_sales_data(sales, filename):
    # Create dr to log sales for debug purposes
    if not os.path.exists('persist/steamsales_history'):
        os.makedirs('persist/steamsales_history')

    # Log specified data
    with open('persist/steamsales_history/' +
              time.strftime('%Y%m%d%H%M', time.localtime()) +
              '-' + filename + '.json', 'w+') as f:
        json.dump(sales, f, sort_keys=True, indent=2)


def get_featured():
    sales_url = "http://store.steampowered.com/api/featured/"
    try:
        sales = http.get_json(sales_url)
    except:
        sales = {}

    if debug:
        log_sales_data(sales, "featured")

    return sales


def get_featuredcategories():
    sales_url = "http://store.steampowered.com/api/featuredcategories/"
    try:
        sales = http.get_json(sales_url)
    except:
        sales = {}

    if debug:
        log_sales_data(sales, "featuredcategories")

    return sales


def get_sales(mask):
    # Fetch data, get it twice to avoid errors - DON'T QUESTION IT
    data = get_featuredcategories()
    flash_data = get_featured()
    data = get_featuredcategories()
    flash_data = get_featured()

    # Break if either return empty - might be unnecessary
    if not data or not flash_data:
        return {}

    # Aggregate data
    fetchtime = int(time.time())
    data["flash"] = {}
    data["flash"]["name"] = "Flash Sales"
    data["flash"]["items"] = []
    data["featured"] = {}
    data["featured"]["name"] = "Featured Sales"
    data["featured"]["items"] = []
    for item in flash_data["large_capsules"]:
        if "discount_expiration" not in item.keys():
            item["discount_expiration"] = 9999999999
        if item["discount_expiration"] - fetchtime <= 28800:
            data["flash"]["items"].append(item)
        else:
            data["featured"]["items"].append(item)

    # Mask Data
    data = {k: v for k, v in data.items() if isinstance(v, dict)
        and k not in mask}

    if debug:
        log_sales_data(data, "data")

    # Format data
    sales = {}
    for category in data:
        #if not data[category]["items"]: sales[data[category]["name"]] = []
        for item in data[category]["items"]:
            # Prepare item data
            try:
                if "url" in item.keys() and "id" not in item.keys():  # Midweek Madness/etc
                    data[category]["name"] = item["name"]
                    appid = str(item["url"])[34:-1]
                    appdata = http.get_json(
                        "http://store.steampowered.com/api/appdetails/?appids={}".format(appid))
                    item["name"] = appdata[appid]["data"]["name"]
                    item["id"] = appdata[appid]["data"]["steam_appid"]
                    if "Free to Play" in appdata[appid]["data"]["genres"]:
                        item["final_price"] = 'Free to Play'
                        item["discount_percent"] = '100'
                    else:
                        item["final_price"] = appdata[appid][
                            "data"]["price_overview"]["final"]
                        item["original_price"] = appdata[appid][
                            "data"]["price_overview"]["initial"]
                        item["discount_percent"] = appdata[appid][
                            "data"]["price_overview"]["discount_percent"]
                    if item["discount_percent"] > 0:
                        item["discounted"] = True
                    else:
                        item["discounted"] = False
                elif set(["id","url"]).issubset(set(item.keys())):
                    # Bundles
                    if not item["final_price"] and not item["discounted"]:
                        item["discounted"] = True
                        item["final_price"] = web.try_isgd(item["url"])
            except:  # Unusuable Catagory e.g. Banner Announcments
                continue
            # Begin work for discounted item
            if item["discounted"]:
                # Clean Item
                item["name"] = item["name"].encode("ascii", "ignore")
                item = {k: str(v) for k, v in item.items() if k in
                    ["name", "final_price", "discount_percent"]}
                # Add item to sales
                if data[category]["name"] not in sales.keys():
                    sales[data[category]["name"]] = []
                sales[data[category]["name"]].append(item)
    sales = {k: sorted(v, key=lambda v: v["name"]) for k, v in sales.items()}

    if debug:
        log_sales_data(sales, "sales")

    # Return usable data
    return sales


def format_sale_item(item):
    if not str(item["final_price"]).isdigit():
        return "\x02{}\x0F: {}".format(item["name"],
            item["final_price"])
    else:
        return "\x02{}\x0F: ${}.{}({}% off)".format(item["name"],
            item["final_price"][:-2],
            item["final_price"][-2:],
            item["discount_percent"])


@hook.singlethread
@hook.command()
def steamsales(inp, say='', chan=''):
    ".steamsales <space seperated options> - Check Steam for specified sales; Displays special event deals on top of chosen deals. Options: daily flash featured specials top_sellers all"
    options = {"Flash Sales": "flash",
               "Featured Sales": "featured",
               "Specials": "specials",
               "Top Sellers": "top_sellers",
               "Daily Deal": "daily",
               "All": "all"}
    mask = ["coming_soon", "new_releases", "genres",
            "trailerslideshow", "status"]

    # Bool flag denoting strict or non-strict masking
    flag = False
    if '-strict' in inp:
        flag = True

    # Clean input data
    inp = [line.strip(', ') for line in inp.lower().split()
        if line in options.values()]

    # Check for bad input
    if not inp:
        return steamsales.__doc__

    # Construct Mask
    if 'all' not in inp:
        mask +=  [option for option in options.values() if option not in inp]

    # Get data
    sales = get_sales(mask)

    # If sales not returned
    if not sales:
        return "Steam Store API error, please try again in a few minutes."

    # Output appropriate data
    if flag:
        sales = {k: v for k, v in sales.items() if options.get(k, '') in inp}
        if not sales:
            return "No specified sales found."

    for category in sales:
        items = [format_sale_item(item) for item in sales[category]]
        if len(items):
            say("\x02{}\x0F: {}".format(category, '; '.join(items)))
        elif category in options.keys():
            say("\x02{}\x0F: {}".format(category, "None found"))


@hook.singlethread
@hook.event('JOIN')
def saleloop(paraml, nick='', conn=None):
    # If specified chan or not running; alter for multi-channel
    if paraml[0] != '#geekboy' or nick != conn.nick:
        return
    mask = ["specials", "coming_soon", "top_sellers", "new_releases",
            "genres", "trailerslideshow", "status"]
    prev_sales = {}
    print(">>> u'Beginning Steam sale check loop :{}'".format(paraml[0]))
    while True:
        try:
            time.sleep(1200)

            # Get data
            sales = get_sales(mask)
            if not sales:
                print(">>> u'Error getting Steam sales :{}'".format(paraml[0]))

            # Handle restarts
            if not prev_sales:
                prev_sales = sales

            # Output appropriate data
            for category in sales:
                items = [format_sale_item(item) for item in sales[category]
                    if item not in prev_sales.get(category, [])]
                if len(items):
                    prev_sales[category] = sales[category]  # Update prev
                    conn.send("PRIVMSG {} :{}".format(paraml[0],
                        "\x02New {}\x0F: {}".format(category, '; '.join(items))))

        except Exception as e:
            print(">>> u'Steam saleloop error: {} :{}'".format(e, paraml[0]))
