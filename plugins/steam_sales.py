"""
steam_sales.py - Written by MikeRixWolfe 2013
"""
import time
import re
import random
import json
from util import hook, http, text
from datetime import datetime

def get_frontpage():
    sales_url = "http://store.steampowered.com/api/featured/"
    sales = http.get_json(sales_url)
    return sales


def get_sales():
    sales_url = "http://store.steampowered.com/api/featuredcategories/"
    sales = http.get_json(sales_url)
    return sales


@hook.command()
def steamsales(inp, say=''):
        ".steamsales <flash|specials|top_sellers|daily> - Check Steam for specified sales; Displays special event deals on top of chosen deals."
        options={"flash": "Flash/Featured Sales", "specials" : "Specials", "top_sellers" : "Top Sellers", "daily" : "Daily Deal"}
    
        # Verify and stage input data
        inp = inp.lower().split()
        inp = [line.strip(', ') for line in inp]
        for i in inp:
            if i not in options.keys():
                inp.remove(i)        

        # Get store data
        data = get_sales()
        flash_data = get_frontpage()
        data["flash"] = {}
        data["flash"]["name"] = "Flash/Featured Sales"
        data["flash"]["items"] = flash_data["large_capsules"]

        # Clean trash data
        del data["coming_soon"], data["new_releases"], data["genres"], data["trailerslideshow"], data["status"]

        # Format data
        sales = {}
        for category in data:
            newkey=data[category]["name"]
            for item in data[category]["items"]:
                if "url" in item.keys() and item["url"] != "":
                    data[category]["name"] = item["name"]
                    appid = str(item["url"])[34:-1]
                    appdata = http.get_json("http://store.steampowered.com/api/appdetails/?appids=%s" % appid)
                    item["name"] = appdata[appid]["data"]["name"]
                    item["final_price"] = appdata[appid]["data"]["price_overview"]["final"]
                    item["discounted"] = True
                    item["discount_percent"]  = appdata[appid]["data"]["price_overview"]["discount_percent"]
                if item["discounted"]:
                    if data[category]["name"] in sales.keys():
                        sales[data[category]["name"]].append(item)
                    else:
                        sales[data[category]["name"]] = []
                        sales[data[category]["name"]].append(item)
            sales[data[category]["name"]] = sorted(sales[data[category]["name"]], key=lambda k: k["name"])
        for key in options:
            if key not in inp:
                del sales[options[key]]

        # Output appropriate data
        for category in sales:
            message = ""
            for item in sales[category]:
                if message == "":
                    message = "\x02New " + category + "\x0F: "
                    message += "\x02%s\x0F: $%s.%s(%s%% off)" % \
                        (item["name"],
                        str(item["final_price"])[:-2],
                        str(item["final_price"])[-2:],
                        str(item["discount_percent"]))
                    message += "; "
            message = message.strip(':; ')
            if message != "\x02New " + category + "\x0F":
                say(message)
            else:
                say("%s: None found" % message)


@hook.event('JOIN')
def saleloop(inp, say='', chan=''):
    # Don't spawn threads for private messages
    if chan[0] != '#':
        return

    print(">>> u'Beginning check for new Steam sales :%s'" % chan)
    prev_sales = {}
    while True:
        # Fetch data
        data = get_sales()
        flash_data = get_frontpage()
        data["flash"] = {}
        data["flash"]["name"] = "Flash/Featured"
        data["flash"]["items"] = flash_data["large_capsules"]
        
        # Mask data
        #del data["flash"]
        del data["specials"], data["coming_soon"], data["top_sellers"], data["new_releases"], data["genres"], data["trailerslideshow"], data["status"]

        # Format data
        sales = {}
        for category in data:
            newkey=data[category]["name"]
            for item in data[category]["items"]:
                if "url" in item.keys() and item["url"] != "":
                    data[category]["name"] = item["name"]
                    appid = str(item["url"])[34:-1]
                    appdata = http.get_json("http://store.steampowered.com/api/appdetails/?appids=%s" % appid)
                    item["name"] = appdata[appid]["data"]["name"]
                    item["final_price"] = appdata[appid]["data"]["price_overview"]["final"]
                    item["discounted"] = True
                    item["discount_percent"]  = appdata[appid]["data"]["price_overview"]["discount_percent"]
                if item["discounted"]:
                    if data[category]["name"] in sales.keys():
                        sales[data[category]["name"]].append(item)
                    else:
                        sales[data[category]["name"]] = []
                        sales[data[category]["name"]].append(item)
            sales[data[category]["name"]] = sorted(sales[data[category]["name"]], key=lambda k: k["name"]) 
        
        # Cut down on spam on bot restarts
        if prev_sales == {}:
            prev_sales = sales

        # Output appropriate data
        for category in sales:
            message = ""
            for item in sales[category]:
                if message == "":
                    message = "\x02New " + category + "\x0F: "
                if item not in (game for category in prev_sales for game in prev_sales[category]):
                    message += "\x02%s\x0F: $%s.%s(%s%% off)" % \
                        (item["name"],
                        str(item["final_price"])[:-2],
                        str(item["final_price"])[-2:],
                        str(item["discount_percent"]))
                    message += "; "
            message = message.strip(':; ')
            if message != "\x02New " + category + "\x0F":
                say(message)
        prev_sales = sales
        time.sleep(1200)
