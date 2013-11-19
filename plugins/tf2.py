"""
tf.py: rewritten by MikeFightsBears 2013, inspired by ipsum
"""

from util import hook, http


@hook.command
def hats(inp):
    """.hats <Steam Vanity URL|Numeric Steam ID> - Shows backpack information for TF2."""

    if inp.isdigit():
        steamid64 = inp
    else:
    	url2 = 'http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key=5519ACA4E3711C3A52AA7CEC7169C6E6&vanityurl=%s' % \
            (http.quote(inp.encode('utf8'), safe=''))
    	try:
	    steamprofile = http.get_json(url2)
    	except KeyError:
	    return '%s is not a valid VANITY URL' % inp
    	try:
	    steamid64 = steamprofile['response']['steamid']
    	except KeyError:
            return '%s is not a valid VANITY URL' % inp



    url = 'http://api.steampowered.com/IEconItems_440/GetPlayerItems/v0001/?SteamID=%s&key=5519ACA4E3711C3A52AA7CEC7169C6E6' % \
        (steamid64)

    #check if profile exists
    try:
        inv = http.get_json(url)
    except ValueError:
        return '%s is not a valid profile' % inp

    total, dropped, dhats, dun, un, hats = 0, 0, 0, 0, 0, 0 
    for x in inv["result"]["items"]:
	total+=1
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

    #get backpack worth
    url3 = 'http://backpack.tf/api/IGetUsers/v2/?steamids=%s&format=json' % \
	(steamid64)
    user_profile = http.get_json(url3)
    backpack_value = user_profile['response']['players']['0']['backpack_value']

#    return '%s  had %s dropped items out of items and %s hats drop (%s hats total), with a backpack worth %s ref' %  \
    return '%s has %s items, %s hats, and %s unusuals (%s/%s/%s of the items/hats/unusals were from drops) and has a backpack worth %s ref' %  \
        (inp, total, hats+dhats, un+dun, dropped, dhats, dun, backpack_value)
