"""
Adapted from Cloudev/Cloudbot's wow armory lookup by Zarthus
"""
import re

from util import hook, http, web


def armory_data(link, format=False):
    """Sends the API request, and returns the data accordingly (in json if raw, nicely formatted if not)."""
    try:
        data = http.get_json(link)
    except Exception as e:
        return 'Unable to fetch information; does the battle tag or character exist?'

    return armory_format(data, link) if format else data


def armory_format(data, link):
    """Format armory data into a human readable string"""

    if len(data) == 0:
        return 'Could not find any results.'

    if 'reason' in data:
        # Something went wrong (i.e. realm does not exist, character does not exist, or page not found).
        return data['reason']

    if 'name' in data:
        niceurl = link.replace('/api/d3/', '/d3/en/')

        try:
            return '{0} is a level \x0307{1}({2})\x0F {3} {4} with \x0307{5}\x0F elite kills ' \
                    'and dealing \x0307{6}\x0F damage. Armory Profile: {7}'.format(data['name'],
                    data['level'], data['paragonLevel'], get_gender(data['gender']),
                    get_class(data['class'], True), data['kills']['elites'], data['stats']['damage'],
                    web.try_googl(niceurl))
        except Exception as e:
            return 'Unable to fetch information; does the realm or character exist?'

    return 'An unexpected error occured.'


def get_gender(gender_id):
    """Formats a gender ID to a readable gender name"""
    gender = 'unknown'

    if gender_id == 0:
        gender = 'male'
    elif gender_id == 1:
        gender = 'female'

    return gender


def get_class(class_id, colours=True):
    """Formats a class ID to a readable name, data from http://eu.battle.net/api/wow/data/character/classes"""
    if colours:
        # Format their colours according to class colours.
        class_ids = {
            "barbarian": "\x0305Barbarian\x0F",
            "witch-doctor": "\x0303Witch Doctor\x0F",
            "crusader": "\x0308Crusader\x0F",
            "wizard": "\x0302Wizard\x0F",
            "monk": "\x02Monk\x0F",
            "demon-hunter": "\x0306Demon Hunter\x0F"
        }
    else:
        class_ids = {
            "barbarian": "Barbarian",
            "witch-doctor": "Witch Doctor",
            "crusader": "Crusader",
            "wizard": "Wizard",
            "monk": "Monk",
            "demon-hunter": "Demon Hunter"
        }

    if class_id in class_ids:
        return class_ids[class_id]
    else:
        return 'unknown'


def region_shortname(region):
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


@hook.command('d3')
@hook.command
def diablo(inp):
    """.diablo [battle-tag] [character name] [region = US] - Look up character and returns API data."""

    # Splits the input, builds the API url, and returns the formatted data to user.
    splitinput = inp.lower().split()

    if len(splitinput) < 2:
        return diablo.__doc__

    battle_tag = splitinput[0].replace('_', '-').replace('#', '-')
    hero_name = splitinput[1]

    # Sets the default region to EU if none specified.
    if len(splitinput) < 3:
        region = 'us'
    else:
        region = splitinput[2]

    if not re.match(r"^[a-z]{1,3}$", region):
        return 'The region specified is not a valid region. Valid regions: eu, us, sea, kr, tw.'

    if re.match(r"^[^\d]$", hero_name) or len(hero_name) > 18:
        # May not contain digits, repeat the same letter three times, or contain non-word characters.
        # Special characters are permitted, such as áéíóßø.
        return 'The character name is not a valid name. Character names can only contain letters, ' \
            'special characters, and be 18 characters long.'

    region_short = region_shortname(region)

    if not region_short:
        return 'The region \'{}\' does not exist.'.format(region)

    career_link = "http://{0}.battle.net/api/d3/profile/{1}/".format(region, battle_tag)

    try:
        career = armory_data(career_link)
        hero_id = [hero for hero in career['heroes'] if hero['name'].lower() == hero_name.lower()][0]['id']
    except:
        return 'Unable to fetch information; does the character exist?'

    hero_link = "http://{0}.battle.net/api/d3/profile/{1}/hero/{2}".format(region, battle_tag, hero_id)

    return armory_data(hero_link, True)

