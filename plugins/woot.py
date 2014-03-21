import time
from util import hook, http, text, web

api = "https://api.woot.com/1/sales/current.rss/"

sites = {"woot": "www.woot.com",
         "wine": "wine.woot.com",
         "sellout": "sellout.woot.com",
         "shirt": "shirt.woot.com",
         "sport": "sport.woot.com",
         "tools": "tools.woot.com",
         "home": "home.woot.com",
         "tech": "tech.woot.com",
         "accessories": "accessories.woot.com"}


def get_woots(inp):
    woots = {}
    for k, v in inp.items():
        try:
            w = {}
            soup = http.get_soup(api + v)

            w['product'] = soup.find('woot:product').text
            w['wootoff'] = soup.find('woot:wootoff').text
            w['price'] = soup.find('woot:price').text
            w['pricerange'] = soup.find('woot:pricerange').text
            w['shipping'] = soup.find('woot:shipping').text
            w['url'] = "http://{}".format(v)
            w['soldout'] = soup.find('woot:soldout').text
            w['soldoutpercent'] =  soup.find('woot:soldoutpercentage').text

            category = text.capitalize_first(k if k == 'woot' else "%s woot" % k)
            if w['wootoff'] != "false":
                category += "off!"

            woots[category] = w
        except:
            continue

    return woots


def format_woot(w):
    if w['soldout'] != "false":
        price = "Soldout!"
    else:
        if w['pricerange'] != w['price'] or '-' in w['price']:
            price = "[{}]".format(w['pricerange'].replace(' ', ''))
        else:
            price = w['price']
        if w['shipping']:
            price += "+%s Shipping" % w['shipping']
        if w['soldoutpercent'] != "0":
            price += " (%s Gone!)" % w['soldoutpercent']

    return "\x02{}\x0F - {} [{}]".format(w['product'], price, w['url'])


@hook.singlethread
@hook.command()
def woot(inp, chan='', say=''):
    ".woot <option> - Gets woots! Options: " \
    "woot wine sellout shirt sport tools home tech accessories"
    # Clean input data
    inp = inp.lower().split(' ')[0]
    inp = {k: v for k, v in sites.items() if k in inp}

    # Check for bad input
    if not inp:
        return woot.__doc__

    # Get data
    woots = get_woots(inp)

    # If sales not returned
    if not woots:
        return "Woot API error, please try again in a few minutes."

    # Output appiropriate data
    for k, v in woots.items():
        say("\x02{}\x0F: {}".format(k, format_woot(v)))


@hook.singlethread
@hook.command(autohelp=False)
def wootlist(inp, nick='', say=''):
    # Get data
    woots = get_woots(sites)
    if not woots:
        return "Error getting Woots, please try again in a few minutes.."

    # Output appiropriate data
    out = []
    for k, v in woots.items():
        out.append("\x02{}\x0F: {}".format(k, v["product"]))
    say("; ".join(out))


@hook.singlethread
@hook.event('JOIN')
def wootloop(paraml, nick='', conn=None):
    # If specified chan or not running; alter for multi-channel
    if paraml[0] != '#geekboy' or nick != conn.nick:
        return
    prev_woots = {}
    print(">>> u'Beginning Woot check loop :{}'".format(paraml[0]))
    while True:
        try:
            time.sleep(600)

            # Get data
            woots = get_woots(sites)
            if not woots:
                print(">>> u'Error getting Woots :{}'".format(paraml[0]))

            # Handle restarts
            if not prev_woots:
                prev_woots = woots

            # Output appiropriate data
            out = []
            for k, v in woots.items():
                if prev_woots.get(k, {}).get("product", {}) != v["product"]:
                    prev_woots[k] = v
                    out.append("\x02New {}\x0F: {}".format(k, v["product"]))
            if out:
                conn.send("PRIVMSG {} :{}".format(paraml[0], "; ".join(out)))
        except Exception as e:
            print(">>> u'Woot saleloop error: {} :{}'".format(e, paraml[0]))
