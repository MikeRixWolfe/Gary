"""
steam_sales.py - Written by MikeRixWolfe 2013
"""

import time
import re
import json
import os
from util import hook, http
from datetime import datetime


running_sale_loops = []


def get_featured():
    sales_url = "http://store.steampowered.com/api/featured/"
    sales = http.get_json(sales_url)

    # Log sales for debug purposes
    with open('persist/steamsales_history/' +
              time.strftime('%Y%m%d%H%M', time.localtime()) +
              '-featured.json', 'w+') as f:
        json.dump(sales, f, sort_keys=False, indent=2)

    return sales


def get_featuredcategories():
    sales_url = "http://store.steampowered.com/api/featuredcategories/"
    sales = http.get_json(sales_url)

    # Log sales for debug purposes
    with open('persist/steamsales_history/' +
              time.strftime('%Y%m%d%H%M', time.localtime()) +
              '-featuredcategories.json', 'w+') as f:
        json.dump(sales, f, sort_keys=False, indent=2)

    return sales


def get_sales(mask, flag=False):
    # Fetch data
    try:
        data = get_featuredcategories()
        flash_data = get_featured()
    except:
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
    if flag:
        data = {k: v for k, v in data.items() if isinstance(v, dict) and v["name"] in mask}
    else:
        data = {k: v for k, v in data.items() if isinstance(v, dict) and k not in mask}

    # Log sales for debug purposes
    with open('persist/steamsales_history/' +
              time.strftime('%Y%m%d%H%M', time.localtime()) +
              '-data.json', 'w+') as f:
        json.dump(data, f, sort_keys=False, indent=2)

    # Format data
    sales = {}
    for category in data:
        for item in data[category]["items"]:
            # Prepare item data
            try:
                if "url" in item.keys() and item["url"]:  # Midweek Madness/etc
                    data[category]["name"] = item["name"]
                    appid = str(item["url"])[34:-1]
                    appdata = http.get_json("http://store.steampowered.com/api/appdetails/?appids={}".format(appid))
                    item["name"] = appdata[appid]["data"]["name"]
                    item["id"] = appdata[appid]["data"]["steam_appid"]
                    
                    if "Free to Play" in appdata[appid]["data"]["genres"]:
                        item["final_price"] = 'Free to Play'
                        item["discount_percent"] = '100'
                    else:
                        item["final_price"] = appdata[appid]["data"]["price_overview"]["final"]
                        item["discount_percent"] = appdata[appid]["data"]["price_overview"]["discount_percent"]
                    #try:
                    #    item["final_price"] = appdata[appid]["data"]["price_overview"]["final"]
                    #except KeyError:
                    #    item["final_price"] = 'Free to Play'
                    #item["discounted"] = True
                    #try:
                    #    item["discount_percent"] = appdata[appid]["data"]["price_overview"]["discount_percent"]
                    #except KeyError:
                    #    item["discount_percent"] = '100'

                    if "discounted" not in item.keys() and item["discount_percent"] > 0:
                        item["discounted"] = True
                    else:
                        item["discounted"] = False
            except:
                continue
            # Begin work for discounted item
            if item["discounted"]:
                # Clean Item
                item["id"] = str(item["id"])
                try:
                    item["name"] = item["name"].encode("ascii", "ignore")
                except:
                    pass
                item = {k: v for k, v in item.items() if k in
                        ["discount_expiration", "discounted",
                        "name", "currency", "final_price",
                        "discount_percent", "id"]}
                # Add item to sales
                if data[category]["name"] not in sales.keys():
                    sales[data[category]["name"]] = []
                sales[data[category]["name"]].append(item)
                    
    sales = {k: sorted(v, key=lambda v: v["name"]) for k, v in sales.items()}

    # Log sales for debug purposes
    with open('persist/steamsales_history/' +
              time.strftime('%Y%m%d%H%M', time.localtime()) +
              '-sales.json', 'w+') as f:
        json.dump(sales, f, sort_keys=False, indent=2)

    # Return usable data
    return sales


def format_sale_item(item):
    if item["final_price"] == 'Free to Play':
        out = "\x02{}\x0F: {}; ".format(item["name"],
              item["final_price"])
    else:
        out = "\x02{}\x0F: ${}.{}({}% off); ".format(item["name"],
              str(item["final_price"])[:-2],
              str(item["final_price"])[-2:],
              str(item["discount_percent"]))
    return out


@hook.singlethread
@hook.command()
def steamsales(inp, say='', chan=''):
    ".steamsales <flash|featured|specials|top_sellers|daily|all> - Check Steam for specified sales; Displays special event deals on top of chosen deals."
    options = {"flash": "Flash Sales",
               "featured": "Featured Sales",
               "specials": "Specials",
               "top_sellers": "Top Sellers",
               "daily": "Daily Deal",
               "all": "All"}
    # Create dr to log sales for debug purposes
    if not os.path.exists('persist/steamsales_history'):
        os.makedirs('persist/steamsales_history')

    # Bool flag denoting strict or non-strict masking
    flag = re.match(r'^.*(-strict).*', inp)

    # Verify and stage input data
    if flag:
        inp = [options[line.strip(', ')] for line in inp.lower().split()
               if line in options.keys()]
    else:
        inp = [line.strip(', ') for line in inp.lower().split()
               if line in options.keys()]

    # Check for bad input
    if not inp:
        return steamsales.__doc__

    # Construct Mask
    mask = ["coming_soon", "new_releases", "genres",
            "trailerslideshow", "status"]
    if any(x in ["all", "All"] for x in inp):
            flag = False
    elif flag:
        mask = inp
    else:
        mask += [option for option in options.keys() if option not in inp]

    # Get data
    try:
        sales = get_sales(mask, flag)
    except Exception as e:
        print(">>> u'Error getting steam sales: {} :{}'".format(e, chan))
        return "Steam Store API error, please try again in a few minutes."

    # Output appropriate data
    for category in sales:
        message = "\x02" + category + "\x0F: "
        for item in sales[category]:
            message += format_sale_item(item)
        message = message.strip(':; ')
        if message != "\x02" + category + "\x0F":
            say(message)
        elif any(x in [k for k, v in options.items() if v == category] for x in inp):
            say("{}: None found".format(message))


#@hook.event('JOIN')
def saleloop(paraml, nick='', conn=None):
    # Don't spawn threads for private messages
    global running_sale_loops
    # Can remove first condition for multi-channel
    if paraml[0] != '#geekboy' or paraml[0] in running_sale_loops:
        return
    running_sale_loops.append(paraml[0])

    # Create dr to log sales for debug purposes
    if not os.path.exists('persist/steamsales_history'):
        os.makedirs('persist/steamsales_history')

    prev_sales = {}
    print(">>> u'Beginning Steam sale check loop :{}'".format(paraml[0]))
    while True:
        try:
            time.sleep(1200)

            # Get data
            mask = ["specials", "coming_soon", "top_sellers", "new_releases",
                    "genres", "trailerslideshow", "status"]
            try:
                sales = get_sales(mask)
            except Exception as e:
                print(">>> u'Error getting Steam sales: {} :{}'".format(e, paraml[0]))
                continue

            # Handle restarts and empty requests
            if prev_sales == {}:
                prev_sales = sales

            # Output appropriate data
            for category in sales:
                message = "\x02New " + category + "\x0F: "
                for item in sales[category]:
                    #if item not in [x for v in prev_sales.values() for x in v]:
                    if item not in (x for v in prev_sales for x in prev_sales[v]):
                        message += format_sale_item(item)
                message = message.strip(':; ')
                if message != "\x02New " + category + "\x0F":
                    out = "PRIVMSG {} :{}".format(paraml[0], message)
                    conn.send(out)

            # Update dict of previous sales if appropriate
            if sales != {}:
                prev_sales = sales

            #print(">>> u'Finished checking for Steam sales :{}'".format(paraml[0]))
        except Exception as e:
            print(">>> u'Steam saleloop error: {} :{}'".format(e,paraml[0]))
            continue

