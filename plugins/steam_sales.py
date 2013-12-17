"""
steam_sales.py - Written by MikeRixWolfe 2013
"""
import time
from util import hook, http
from datetime import datetime

running_sale_loops = []

def get_featured():
    sales_url = "http://store.steampowered.com/api/featured/"
    sales = http.get_json(sales_url)
    return sales


def get_featuredcategories():
    sales_url = "http://store.steampowered.com/api/featuredcategories/"
    sales = http.get_json(sales_url)
    return sales
    

def get_sales(mask_items):
    # Fetch data
    try:
        data = get_featuredcategories()
        flash_data = get_featured()
    except:
        return {}
        
    # Aggregate data
    data["flash"] = {}
    data["flash"]["name"] = "Flash/Featured Sales"
    data["flash"]["items"] = flash_data["large_capsules"]

    # Mask Data
    for item in mask_items:
        del data[item]
        
    # Format data
    sales = {}
    for category in data:
        for item in data[category]["items"]:
            if "url" in item.keys() and item["url"] != "":
                data[category]["name"] = item["name"]
                appid = str(item["url"])[34:-1]
                appdata = http.get_json("http://store.steampowered.com/api/appdetails/?appids=%s" % appid)
                item["name"] = appdata[appid]["data"]["name"]
                item["id"] = appdata[appid]["data"]["steam_appid"]
                item["final_price"] = appdata[appid]["data"]["price_overview"]["final"]
                item["discounted"] = True
                item["discount_percent"]  = appdata[appid]["data"]["price_overview"]["discount_percent"]
            if item["discounted"]:
                item["id"] = str(item["id"]) # The ID's steam returns are not a consistant type, wtf right?
                if data[category]["name"] in sales.keys():
                    sales[data[category]["name"]].append(item)
                else:
                    sales[data[category]["name"]] = []
                    sales[data[category]["name"]].append(item)
        sales[data[category]["name"]] = sorted(sales[data[category]["name"]], key=lambda k: k["name"])
    
    # Return usable data
    return sales

    
@hook.command()
def steamsales(inp, say=''):
    ".steamsales <flash|specials|top_sellers|daily|all> - Check Steam for specified sales; Displays special event deals on top of chosen deals."
    options={"flash": "Flash/Featured Sales", "specials" : "Specials", "top_sellers" : "Top Sellers", "daily" : "Daily Deal", "all" : "All"}

    # Verify and stage input data
    inp = inp.lower().split()
    inp = [line.strip(', ') for line in inp]
    for i in inp:
        if i not in options.keys():
            inp.remove(i)
    
    # Check for bad input
    if inp == []: 
        return steamsales.__doc__

    # Get data
    mask = ["coming_soon","new_releases","genres","trailerslideshow","status"]
    sales = get_sales(mask)
    
    # Mask data for users request
    if "all" not in inp:
        for key in options:
            if key not in inp and options[key] in sales.keys():
                del sales[options[key]]

    # Output appropriate data
    for category in sales:
        message = ""
        for item in sales[category]:
            if message == "":
                message = "\x02" + category + "\x0F: "
            message += "\x02%s\x0F: $%s.%s(%s%% off)" % \
                (item["name"],
                str(item["final_price"])[:-2],
                str(item["final_price"])[-2:],
                str(item["discount_percent"]))
            message += "; "
        message = message.strip(':; ')
        if message != "\x02" + category + "\x0F":
            say(message)
        else:
            say("%s: None found" % message)
    
    
@hook.event('JOIN')
@hook.command()
def saleloop(paraml, conn=None):
    # Don't spawn threads for private messages
    global running_sale_loops
    if paraml[0][0] != '#' or paraml[0] in running_sale_loops:
        return
    running_sale_loops.append(paraml[0])
    prev_sales = {}

    while True:
        #time.sleep(1200)
        print(">>> u'Beginning check for new Steam sales :%s'" % paraml[0])

        # Get data
        mask = ["specials","coming_soon","top_sellers","new_releases","genres","trailerslideshow","status"]
        sales = get_sales(mask)

        # Cut down on spam on bot restarts
        if prev_sales == {}:
            prev_sales = sales

        # Output appropriate data
        for category in sales:
            message = ""
            for item in sales[category]:
                if message == "":
                    message = "\x02New " + category + "\x0F: "
                if str(item["id"]) not in (game["id"] for category in prev_sales for game in prev_sales[category]):
                    message += "\x02%s\x0F: $%s.%s(%s%% off)" % \
                        (item["name"],
                        str(item["final_price"])[:-2],
                        str(item["final_price"])[-2:],
                        str(item["discount_percent"]))
                    message += "; "
            message = message.strip(':; ')
            if message != "\x02New " + category + "\x0F":
                out = "PRIVMSG {} :{}".format(paraml[0], message)
                conn.send(out)

        # Update dict of previous sales if appropriate
        if sales != {}:
            prev_sales = sales
        print(">>> u'Finished check for new Steam sales :%s'" % paraml[0])
        time.sleep(1200)

