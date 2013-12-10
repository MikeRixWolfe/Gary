"""
steam_sales.py - Written by MikeRixWolfe 2013
"""
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


@hook.command(autohelp=False)
def steamsales(inp, say=''):
    ".steamsales - Gets current Specials, Daily Deals, and Spotlight (if any exist)."
    try:
        data = get_sales()
    except:
        return "Steam API error; unable to access sales information."
    
    del data["coming_soon"]
    del data["top_sellers"]
    del data["new_releases"]
    del data["genres"]
    del data["trailerslideshow"]
    del data["status"]

    sales = {}
    for item in data:
        newkey=data[item]["name"]
        newval=data[item]["items"]
        sales[newkey]=newval

    for category in sales:
        message = category + ": "
        for item in sales[category]:
            if item["name"] != "":
                message += "\x02%s\x0F: $%s.%s(%s%% off); " % \
                    (item["name"], 
                    str(item["final_price"])[:-2], 
                    str(item["final_price"])[-2:], 
                    str(item["discount_percent"]))
        if message != "%s: " % category:
            say(message.strip('; '))



@hook.command(autohelp=False)
def flashsales(inp, say=''):
    ".flashsales - Gets current Flash Sales (if any exist) or Featured Sales."
    #previous_data = {}
    #while True:
    try:
        data = get_frontpage()

        del data["featured_win"]
        del data["featured_mac"]
        del data["layout"]
        del data["status"]
    
        #if data.keys() != previous_data.keys():
        category = "Flash Sales"
        message = category + ": "
        for item in data["large_capsules"]:
            if item["name"] != "" and item["discounted"]:
                message += "\x02%s\x0F: $%s.%s(%s%% off); " % \
                    (item["name"],
                    str(item["final_price"])[:-2],
                    str(item["final_price"])[-2:],
                    str(item["discount_percent"]))
        if message != "%s: " % category:
            say(message.strip('; '))
        else:
            say("There are currently no flash sales")
        #previous_data = data
    except:
        #do = "nothing"
        return "Steam API error; unable to access sales information."
    #time.sleep(1200)
