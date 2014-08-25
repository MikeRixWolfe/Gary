import json
from util import hook, http, web

user_url = "http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key=%s&vanityurl=%s"
profile_url = "http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key=%s&steamids=%s"
account_url = "http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key=%s&steamid=%s&format=json"
games_url = "http://store.steampowered.com/api/appdetails/?appids=%s"


@hook.singlethread
@hook.api_key('steam_key')
@hook.command(autohelp=True)
def steamcalc(inp, say='', api_key=None):
    """.steamcalc <Steam Vanity URL ID> - Gets Steam account value for a given Vanity ID. Uses steamcommunity.com/id/<nickname>."""
    # Get SteamID
    try:
        steamid = http.get_json(user_url % (api_key, http.quote(inp.encode('utf8'), safe='')))['response']['steamid']
    except:
        return "'%s' does not appear to be a valid Vanity ID. Uses steamcommunity.com/id/<VanityID>." % inp

    # Get Steam profile info
    try:
        profile = http.get_json(profile_url % (api_key, steamid))['response']['players'][0]
        persona = profile['personaname']
    except:
        return "Error looking up %s's Steam profile." % inp

    # Get Steam account games for User
    try:
        account = http.get_json(account_url % (api_key, steamid))['response']['games']
        games = [str(item['appid']) for item in account]
    except:
        return "Error looking up %s's Steam inventory." % inp

    # Get info for games
    say("Collecting data for %s, please wait..." % inp)
    games_info = {}
    try:
        while games:
            games_temp, games = games[:20], games[20:]
            gurl = games_url % ','.join(games_temp)
            games_info  = dict(games_info.items() + http.get_json(gurl).items())
    except:
        return "Error looking up game data, please try again later."

    # Aggregate Steam data
    prices = []
    scores = []
    for game in games_info:
        try:
            prices.append(games_info[game]['data']['price_overview']['final'])
            scores.append(games_info[game]['data']['metacritic']['score'])
        except:
            pass #print games_info[game]

    prices = [int(price) / 100. for price in prices]
    scores = [float(score) for score in scores]

    total_price = "{0:.2f}".format(sum(prices))
    avg_score = "{0:.1f}".format(sum(scores) / len(scores))

    say("{} has {} games with a total value of ${} and an average metascore of {}".format(persona, len(games_info), total_price, avg_score))
