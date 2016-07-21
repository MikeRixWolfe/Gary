"""
Via Cloudev/Cloudbot

wow.py:
Written by Zarthus <zarthus@zarth.us> May 30, 2014.
Gets data from the World of Warcraft Armory API

Commands:
armory, armory: Request data from the armory API and format it into something human readable.
"""

import re

from util import hook, http, web


def wow_armory_data(link, api_key):
    """Sends the API request, and returns the data accordingly (in json if raw, nicely formatted if not)."""
    try:
        data = http.get_json(link, fields='items,titles,talents,guild', locale='en_US', apikey=api_key['consumer'])
    except Exception as e:
        return 'Unable to fetch information; do the realm and character exist?'

    return wow_armory_format(data, link)


def wow_armory_format(data, link):
    """Format armory data into a human readable string"""
    if len(data) == 0:
        return 'Could not find any results.'

    if 'reason' in data:
        # Something went wrong (i.e. realm does not exist, character does not exist, or page not found).
        return data['reason']

    if 'name' in data:
        niceurl = link.replace('api.battle.net', 'battle.net').replace('/api/wow/', '/wow/en/').replace('\'', '') + '/simple'

    if 'guild' in data:
        location = "in {} on {}".format(data['guild']['name'], data['realm'])
    else:
        location = "on {}".format(data['realm'])

    try:
        return u'\x0307{0}\x0F is a level \x0307{1}(ilvl {8}/{9})\x0F {2} {10} {3} {4} with ' \
            '\x0307{5}\x0F achievement points and \x0307{6}\x0F honourable kills. Armory Profile: {7}' \
            .format(wow_get_title(data), data['level'], wow_get_gender(data['gender']), wow_get_class(data, True),
                    location, data['achievementPoints'], data['totalHonorableKills'], web.try_googl(niceurl),
                    data['items']['averageItemLevelEquipped'], data['items']['averageItemLevel'],
                    wow_get_race(data['race']))
    except:
        try:
            return "Error: {}".format(data['reason'])
        except:
            return 'Unable to fetch information; do the realm and character exist?'


def wow_get_title(data):
    """Gets the the active title"""
    try:
        return [title for title in data['titles'] if title.get('selected', False) == True][0]['name'] % data['name']
    except:
        return data['name']


def wow_get_gender(gender_id):
    """Formats a gender ID to a readable gender name"""
    gender = 'unknown'

    if gender_id == 0:
        gender = 'male'
    elif gender_id == 1:
        gender = 'female'

    return gender


def wow_get_class(data, colours=False):
    """Formats a class ID to a readable name, data from http://us.api.battle.net/wow/data/character/classes"""
    try:
        spec = [s for s in data['talents'] if s.get('selected', False) == True][0]['spec']['name']
    except:
        spec = ""

    if colours:
        # Format their colours according to class colours.
        class_ids = {
            1: "\x0304{} Warrior\x0F", 2: "\x0313{} Paladin\x0F", 3: "\x0309{} Hunter\x0F", 4: "\x0308{} Rogue\x0F",
            5: "\x02{} Priest\x0F", 6: "\x0305{} Death Knight\x0F", 7: "\x0312{} Shaman\x0F", 8: "\x0311{} Mage\x0F",
            9: "\x0306{} Warlock\x0F", 10: "\x0310{} Monk\x0F", 11: "\x0307{} Druid\x0F", 12: "\x0303{} Demon Hunter\x0F"
        }
    else:
        class_ids = {
            1: "{} Warrior", 2: "{} Paladin", 3: "{} Hunter", 4: "{} Rogue", 5: "{} Priest",
            6: "{} Death Knight", 7: "{} Shaman", 8: "{} Mage", 9: "{} Warlock", 10: "{} Monk",
            11: "{} Druid", 12: "{} Demon Hunter"
        }

    if data['class'] in class_ids:
        return class_ids[data['class']].format(spec).strip()
    else:
        return 'unknown'


def wow_get_race(race_id):
    """Formats a race ID to a readable race name, data from http://us.api.battle.net/wow/data/character/races"""
    race_ids = {
        1: "Human", 2: "Orc", 3: "Dwarf", 4: "Night Elf", 5: "Undead", 6: "Tauren", 7: "Gnome",
        8: "Troll", 9: "Goblin", 10: "Blood Elf", 11: "Draenei", 22: "Worgen",
        24: "Pandaren (neutral)", 25: "Pandaren (Alliance)", 26: "Pandaren (Horde)"
    }

    if race_id in race_ids:
        return race_ids[race_id]
    else:
        return 'unknown'


def wow_region_shortname(region):
    """Returns a short region name, which functions as battle.net their subdomain (i.e. eu.battle.net)"""
    valid_regions = {
        'eu': 'eu', 'europe': 'eu',
        'us': 'us',
        'sea': 'sea', 'asia': 'sea',
        'kr': 'kr', 'korea': 'kr',
        'tw': 'tw', 'taiwan': 'tw'
    }

    if region in valid_regions:
        return valid_regions[region]
    else:
        return False


@hook.api_key('mashery')
@hook.command('wow')
@hook.command
def armory(inp, say=None, api_key=None):
    """.armory/.wow <realm> <character name> [region = US] - Look up character and returns API data."""
    if not isinstance(api_key, dict) or any(key not in api_key for key in ('consumer', 'consumer_secret')):
        return "Error: API keys not set."

    # Splits the input, builds the API url, and returns the formatted data to user.
    splitinput = inp.lower().split()

    if len(splitinput) < 2:
        return 'armory [realm] [character name] [region = US] - Look up character and returns API data.'

    realm = splitinput[0].replace('_', '-')
    char_name = splitinput[1]

    # Sets the default region to EU if none specified.
    if len(splitinput) < 3:
        region = 'us'
    else:
        region = splitinput[2]

    if not re.match(r"^[a-z]{1,3}$", region):
        return 'The region specified is not a valid region. Valid regions: eu, us, sea, kr, tw.'

    if re.match(r"^[^\d]$", char_name) or len(char_name) > 18:
        # May not contain digits, repeat the same letter three times, or contain non-word characters.
        # Special characters are permitted, such as áéíóßø.
        return 'The character name is not a valid name. Character names can only contain letters, special characters,' \
               ' and be 18 characters long.'

    if not re.match(r"^[a-z' _-]{3,32}$", realm):
        # Realm names can have spaces in them, use dashes for this.
        return 'The realm name is not a valid name. Realm names can only contain letters, dashes, and apostrophes, up' \
               ' to 32 characters'

    region_short = wow_region_shortname(region)

    if not region_short:
        return 'The region \'{}\' does not exist.'.format(region)

    link = u"https://{0}.api.battle.net/wow/character/{1}/{2}".format(region, realm, char_name)

    say(wow_armory_data(link, api_key))

