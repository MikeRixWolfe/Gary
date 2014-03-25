"""
tf.py: written by MikeFightsBears 2013, inspired by ipsum
"""

from util import hook, http

steam_key = '5519ACA4E3711C3A52AA7CEC7169C6E6'

#@hook.api_key('steam_key')
@hook.command
def hats(inp):
    ".hats <Steam Vanity URL|Numeric Steam ID> - Shows backpack information for TF2."

    # Get SteamID
    if inp.isdigit():
        steamid64 = inp
    else:
        try:
            id_url = 'http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key=%s&vanityurl=%s' % \
                (steam_key, http.quote(inp.encode('utf8'), safe=''))
            steamid64 = http.get_json(id_url)['response']['steamid']
        except:
            return "Error getting numeric Steam ID, please try format '.hats <Numeric Steam ID>'"

    # Get Steam User's TF2 Inventory/Check for User
    try:
        inv_url = 'http://api.steampowered.com/IEconItems_440/GetPlayerItems/v0001/?SteamID=%s&key=%s' % \
            (steamid64, steam_key)
        inv = http.get_json(inv_url)
    except:
        return "Sorry, I couldn't find '%s''s Steam inventory." % inp

    # Count Items into Categories
    total, dropped, dhats, dun, un, hats = 0, 0, 0, 0, 0, 0
    for x in inv["result"]["items"]:
        total += 1
        ind = int(x['defindex'])
        if x['origin'] == 0:
            if x['quality'] == 5:
                dun += 1
            if 47 <= ind <= 55 or 94 <= ind <= 126 or 134 <= ind <= 152:
                dhats += 1
            else:
                dropped += 1
        else:
            if x['quality'] == 5:
                un += 1
            if 47 <= ind <= 55 or 94 <= ind <= 126 or 134 <= ind <= 152:
                hats += 1

    # Get Market Price for Backpack
    try:
        backpack_url = 'http://backpack.tf/api/IGetUsers/v3/?steamids=%s&format=json' % \
            (steamid64)
        backpack = http.get_json(backpack_url)
        ref = backpack['response']['players'][0]['backpack_value']['440']
    except:
        ref = '???'

    return '%s has %s items, %s hats, and %s unusuals (%s/%s/%s of the ' \
        'items/hats/unusals were from drops) and has a backpack worth %s ref' %  \
        (inp, total, hats + dhats, un + dun, dropped, dhats, dun, ref)
