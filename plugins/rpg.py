"""
   ()
   )(
o======o
   ||
   ||    ___              _            _ _        ____                 _
   ||   / _ \___ _ __ ___(_)_   ____ _| ( )__    /___ \_   _  ___  ___| |_
   ||  / /_)/ _ \ '__/ __| \ \ / / _` | |/ __|  //  / / | | |/ _ \/ __| __|
   || / ___/  __/ | | (__| |\ V / (_| | |\__ \ / \_/ /| |_| |  __/\__ \ |_
   || \/    \___|_|  \___|_| \_/ \__,_|_||___/ \___,_\ \__,_|\___||___/\__|
   ||
   ||                           copyright 2013
   ||
   \/

"""

import namegen
import random
import shelve
from util import hook
import os
import re
import time


dclasses = {
    'fighter': {'stat': (5, 3, 2, 4, 0, 1), 'skill': 'Trip'},
    'paladin': {'stat': (5, 3, 0, 4, 2, 1), 'skill': 'Smite'},
    'ranger': {'stat': (4, 5, 3, 2, 1, 0), 'skill': 'Doublestrike'},
    'cleric': {'stat': (2, 5, 0, 1, 3, 4), 'skill': 'Cure'},
    'rogue': {'stat': (3, 2, 5, 0, 1, 4), 'skill': 'Backstab'},
    'bard': {'stat': (1, 2, 5, 0, 4, 3), 'skill': 'Charm'},
    'barbarian': {'stat': (4, 3, 2, 5, 1, 0), 'skill': 'Rage'},
    'druid': {'stat': (1, 2, 0, 5, 3, 4), 'skill': 'Entangle'},
    'monk': {'stat': (3, 4, 2, 0, 5, 1), 'skill': 'Evade'},
    'wizard': {'stat': (0, 2, 3, 1, 4, 5), 'skill': 'Missile'}}

draces = {
    'human': {'stat': (0, 0, 0, 0, 0, 0), 'ben': 'Bonus feat'},
    'dwarf': {'stat': (0, 0, 0, 1, 1, 0), 'ben': '+1 Fortitude, +1 Mind'},
    'elf': {'stat': (0, 0, 1, 0, 0, 1), 'ben': '+1 Reflexes, +1 Skill'},
    'halfling': {'stat': (0, 1, 1, 0, 0, 0), 'ben': '+1 Defense, +1 Reflexes'},
    'gnome': {'stat': (0, 0, 0, 1, 0, 1), 'ben': '+1 Fortitude, +1 Skill'},
    'orc': {'stat': (1, 1, 0, 0, 0, 0), 'ben': '+1 Attack, +1 Defense'},
    'drow': {'stat': (1, 0, 0, 0, 1, 0), 'ben': '+1 Attack, +1 Mind'}}

dfeats = {'PowerAttack': 0, 'StoutDefense': 1, 'LightningReflexes': 2,
          'Toughness': 3, 'IronWill': 4, 'Prodigy': 5, 'ImprovedInitiative': -1}

dmonst = {
    1: {'goblin': {'stat': (0, 0, 0, 0, 0, 0), 'skill': 'Flee'},
        'troglodyte': {'stat': (1, 0, 1, 1, 0, 0), 'skill': 'Poison'},
        'skeleton': {'stat': (1, 1, 0, 0, 1, 0), 'skill': 'Fear'}},
    2: {'bugbear': {'stat': (2, 1, 0, 1, 0, 0), 'skill': 'Rage'},
        'imp': {'stat': (0, 0, 2, 0, 1, 1), 'skill': 'Charm'},
        'worg': {'stat': (1, 1, 1, 1, 0, 0), 'skill': 'Trip'}},
    3: {'cockatrice': {'stat': (1, 2, 0, 1, 1, 0), 'skill': 'Petrify'},
        'ogre': {'stat': (3, 1, 0, 1, 0, 0), 'skill': 'Smite'},
        'wight': {'stat': (1, 1, 1, 0, 1, 2), 'skill': 'Fear'}},
    4: {'ettin': {'stat': (3, 1, 0, 2, 0, 0), 'skill': 'Doublestrike'},
        'manticore': {'stat': (2, 2, 0, 1, 0, 1), 'skill': 'Missile'},
        'wyvern': {'stat': (1, 1, 2, 1, 0, 1), 'skill': 'Poison'}},
    5: {'succubus': {'stat': (1, 1, 2, 1, 0, 1, 2), 'skill': 'Charm'},
        'gorgon': {'stat': (2, 2, 0, 2, 0, 2), 'skill': 'Petrify'},
        'ogre mage': {'stat': (3, 0, 0, 1, 1, 3), 'skill': 'Missile'}},
    6: {'frost giant': {'stat': (4, 2, 0, 2, 2, 0), 'skill': 'Smite'},
        'rakshasa': {'stat': (2, 2, 1, 1, 1, 3), 'skill': 'Entangle'},
        'hydra': {'stat': (5, 2, 0, 3, 0, 0), 'skill': 'Doublestrike'}},
    7: {'kraken': {'stat': (5, 3, 0, 4, 0, 0), 'skill': 'Trip'},
        'stone golem': {'stat': (3, 4, 0, 3, 2, 0), 'skill': 'Evade'},
        'purple worm': {'stat': (5, 2, 0, 3, 0, 2), 'skill': 'Poison'}},
    8: {'astral deva': {'stat': (4, 2, 1, 2, 2, 3), 'skill': 'Fear'},
        'storm giant': {'stat': (5, 2, 1, 2, 2, 3), 'skill': 'Smite'},
        'nightshade': {'stat': (3, 4, 1, 3, 0, 3), 'skill': 'Backstab'}},
    9: {'marilith': {'stat': (4, 3, 2, 3, 2, 2), 'skill': 'Doublestrike'},
        'pit fiend': {'stat': (5, 3, 1, 3, 3, 2), 'skill': 'Poison'},
        'tarrasque spawn': {'stat': (6, 5, 0, 5, 0, 0), 'skill': 'Smite'}}}

dstats = {
    'Attack': 0,
    'Defense': 1,
    'Reflexes': 2,
    'Fortitude': 3,
    'Mind': 4,
    'Skill': 5,
    0: 'Attack', 1: 'Defense', 2: 'Reflexes', 3: 'Fortitude', 4: 'Mind', 5: 'Skill'}
dst = {0: 'Atk', 1: 'Def', 2: 'Ref', 3: 'Frt', 4: 'Mnd', 5: 'Skl'}

dtreas = {
    'ring': {'Protection': 'Evade', 'Fury': 'Smite', 'Subtlety': 'Backstab',
             'Regeneration': 'Cure', 'Glibness': 'Charm', 'Webs': 'Entangle',
             'Force': 'Missile', 'Speed': 'Doublestrike', 'Berserking': 'Rage',
             'Venom': 'Poison', 'Avoidance': 'Flee', 'Intimidation': 'Fear',
             'Basilisk': 'Petrify'},
    'armor': {'Caster': {'Masterwork': 1, 'Spidersilk': 2, 'Enchanted': 3},
              'Cloth': {'Masterwork': 1, 'Thistledown': 2, 'Twilight': 3},
              'Leather': {'Masterwork': 1, 'Leafweave': 2, 'Dragonhide': 3},
              'Mail': {'Masterwork': 1, 'Mithril': 2, 'Adamantine': 3}},
    'rarmor': {'Caster': {1: 'Masterwork', 2: 'Spidersilk', 3: 'Enchanted'},
               'Cloth': {1: 'Masterwork', 2: 'Thistledown', 3: 'Twilight'},
               'Leather': {1: 'Masterwork', 2: 'Leafweave', 3: 'Dragonhide'},
               'Mail': {1: 'Masterwork', 2: 'Mithril', 3: 'Adamantine'}},
    'weapon': {'Swords': {'Masterwork': 1, 'Keen': 2, 'Vorpal': 3},
               'Axes': {'Masterwork': 1, 'Wounding': 2, 'Vicious': 3},
               'Polearms': {'Masterwork': 1, 'Lunging': 2, 'Valorous': 3},
               'Clubs': {'Masterwork': 1, 'Impactful': 2, 'Dolorous': 3},
               'Whips': {'Masterwork': 1, 'Animated': 2, 'Dancing': 3}},
    'rweapon': {'Swords': {1: 'Masterwork', 2: 'Keen', 3: 'Vorpal'},
                'Axes': {1: 'Masterwork', 2: 'Wounding', 3: 'Vicious'},
                'Polearms': {1: 'Masterwork', 2: 'Lunging', 3: 'Valorous'},
                'Clubs': {1: 'Masterwork', 2: 'Impactful', 3: 'Dolorous'},
                'Whips': {1: 'Masterwork', 2: 'Animated', 3: 'Dancing'}}}

dgear = {
    'armor': {'Caster': {'Sack': 0, 'Robes': 1, 'Vestment': 2, 'Bolero': 3, 'Habit': 4, 'Djellaba': 5},
              'Cloth': {
                  'Shirt': 0,
                  'Jerkin': 1,
                  'Vest': 2,
                  'Padded': 3,
                  'Gi': 4,
                  'Mantle': 5},
              'Leather': {
                  'Loincloth': 0,
                  'Hide': 1,
                  'Studded': 2,
                  'Brigandine': 3,
                  'Lamellar': 4,
                  'Banded': 5},
              'Mail': {'Barrel': 0, 'Splintmail': 1, 'Chainmail': 2, 'Scalemail': 3, 'Breastplate': 4, 'Platemail': 5}},
    'rarmor': {'Caster': {0: 'Sack', 1: 'Robes', 2: 'Vestment', 3: 'Bolero', 4: 'Habit', 5: 'Djellaba'},
               'Cloth': {
                   0: 'Shirt',
                   1: 'Jerkin',
                   2: 'Vest',
                   3: 'Padded',
                   4: 'Gi',
                   5: 'Mantle'},
               'Leather': {
                   0: 'Loincloth',
                   1: 'Hide',
                   2: 'Studded',
                   3: 'Brigandine',
                   4: 'Lamellar',
                   5: 'Banded'},
               'Mail': {0: 'Barrel', 1: 'Splintmail', 2: 'Chainmail', 3: 'Scalemail', 4: 'Breastplate', 5: 'Platemail'}},
    'weapon': {'Swords': {'Dagger': 0, 'Machete': 1, 'Rapier': 2, 'Longsword': 3, 'Falchion': 4, 'Claymore': 5},
               'Axes': {
                   'Cleaver': 0,
                   'Hatchet': 1,
                   'Battleaxe': 2,
                   'Waraxe': 3,
                   'Lochaber': 4,
                   'Greataxe': 5},
               'Polearms': {
                   'Broom': 0,
                   'Quarterstaff': 1,
                   'Spear': 2,
                   'Pike': 3,
                   'Glaive': 4,
                   'Halberd': 5},
               'Clubs': {
                   'Sap': 0,
                   'Club': 1,
                   'Truncheon': 2,
                   'Warhammer': 3,
                   'Greatclub': 4,
                   'Maul': 5},
               'Whips': {'Rope': 0, 'Whip': 1, 'Chain': 2, 'Flail': 3, 'Kusarigama': 4, 'Dragonfist': 5}},
    'rweapon': {'Swords': {0: 'Dagger', 1: 'Machete', 2: 'Rapier', 3: 'Longsword', 4: 'Falchion', 5: 'Claymore'},
                'Clubs': {
                    0: 'Sap',
                    1: 'Club',
                    2: 'Truncheon',
                    3: 'Warhammer',
                    4: 'Greatclub',
                    5: 'Maul'},
                'Axes': {
                    0: 'Cleaver',
                    1: 'Hatchet',
                    2: 'Battleaxe',
                    3: 'Waraxe',
                    4: 'Lochaber',
                    5: 'Greataxe'},
                'Polearms': {
                    0: 'Broom',
                    1: 'Quarterstaff',
                    2: 'Spear',
                    3: 'Pike',
                    4: 'Glaive',
                    5: 'Halberd'},
                'Whips': {0: 'Rope', 1: 'Whip', 2: 'Chain', 3: 'Flail', 4: 'Kusarigama', 5: 'Dragonfist'}}}

dprice = (1, 10, 100, 500, 1000, 5000, 10000, 50000, 100000)

dskill = {
    'Bronze': 'Evade',
    'Gold': 'Smite',
    'Blue': 'Backstab',
    'Silver': 'Cure',
    'Brass': 'Charm',
    'Green': 'Entangle',
    'Force': 'Missile',
    'Mercury': 'Doublestrike',
    'Red': 'Rage',
    'Black': 'Poison',
    'White': 'Flee',
    'Bone': 'Fear',
    'Stone': 'Petrify'}


def drating(type, item):
    txt = item.split()
    res = 0
    for i in txt:
        res += dgear[type[0]][type[1]
                              ].get(i, 0) + dtreas[type[0]][type[1]].get(i, 0)
    return res


def treasuregen(level):
    treas = {'armor': '', 'weapon': '', 'gp': 0}
    treas['gp'] = random.randint(0, 10 * level)  # roll for gp
    carm = random.randint(1, 10)  # roll for armor
    if carm <= level:
        typ = random.choice(dgear['armor'].keys())
        maxrat = min([level / 2 + 1, 5])
        rat = random.randint(1, maxrat)
        marm = random.randint(1, 10)  # roll for magic
        mag = ''
        if marm <= level:
            maxmag = min([level / 3, 3])
            mag = dtreas['rarmor'][typ].get(random.randint(0, maxmag), '')
            if mag:
                mag += ' '
        treas['armor'] = mag + dgear['rarmor'][typ][rat]
    cwep = random.randint(1, 10)  # roll for weapon
    if cwep <= level:
        typ = random.choice(dgear['weapon'].keys())
        maxrat = min([level / 2, 5])
        rat = random.randint(0, maxrat)
        mwep = random.randint(1, 10)  # roll for magic
        mag = ''
        if mwep <= level:
            maxmag = min([level / 3, 3])
            mag = dtreas['rweapon'][typ].get(random.randint(0, maxmag), '')
            if mag:
                mag += ' '
        treas['weapon'] = mag + dgear['rweapon'][typ][rat]
    crin = random.randint(3, 15)  # roll for ring
    if crin <= level:
        treas['ring'] = random.choice(dtreas['ring'].keys())
    return treas


def item_type(item):
    if item in dtreas['ring'].keys():
        return ['ring']
    itm = item.split()
    for i in itm:
        for j in dgear['armor'].keys():
            for k in dgear['armor'][j].keys():
                if i.lower() == k.lower():
                    return ['armor', j]
        for j in dgear['weapon'].keys():
            for k in dgear['weapon'][j].keys():
                if i.lower() == k.lower():
                    return ['weapon', j]
    return None


def item_worth(item):
    typ = item_type(item)
    if typ[0] == 'ring':
        return 3000
    elif typ:
        return dprice[drating(typ, item)]
    else:
        return 0


def collapse_list(tmp, srt=False):
    ret = []
    [ret.append(i) for i in tmp if not ret.count(i)]
    if srt:
        ret = sorted(ret)
    return ret


class dPuzzle:

    def __init__(self, lvl):
        riddle = namegen.riddlegen()
        self.answer = riddle[0]
        self.riddle = riddle[1]
        self.riddleguess = 3
        riches = []
        while not riches:
            tr = treasuregen(lvl + 2)
            for t in tr.keys():
                if t == 'gp':
                    continue
                if tr[t]:
                    riches.append(tr[t])
        self.riches = random.choice(riches)
        self.numcode = namegen.numgen()
        self.numguess = 10
        self.gold = tr['gp'] * 100
        self.damage = 0
        self.tnum = lvl
        self.knowledge = lvl / 2
        self.thing = random.choice(
            ['mysterious dark spirit', 'regal sphinx', 'magic mirror', 'blind oracle'])
        self.choice = ""

    def puzzlemsg(self, input=None):
        msg1 = "Exploring the depths of the Dungeon, you encounter a " + \
            self.thing + " in a lonely room."
        if self.thing == 'magic mirror':
            msg1 += " A sinister face materializes in its murky surface, looking directly at you."
        else:
            msg1 += " The " + self.thing + " addresses you."
        msg2 = "'Welcome to the Dungeon, adventurer. Portents have foreshadowed your coming. I am here to aid you on your journey, should you prove worthy."
        msg2 += " I offer you choices three: you may play a game, for Gold; solve a riddle, for Riches; or undergo a Trial of Being, for Knowledge. Choose your prize, and choose well.'"
        msg3 = "(Use .rpgpuzzle to make your choice {gold, riches, knowledge, or skip}, and for further interactions.)"
        input.conn.msg(input.chan, msg1)
        input.conn.msg(input.chan, msg2)
        input.conn.msg(input.chan, msg3)

    def puzzleinit(self, input, rpg, choice):
        self.choice = choice.lower()
        if self.choice == "gold":
            msg = "The " + self.thing + \
                " nods approvingly. 'You have chosen the game; here are the rules. I have selected a set of four digits, in some order. "
            msg += "You have 10 chances to guess the digits, in the correct order. If you are polite, I may be persuaded to give you a hint... Now, begin; you have 10 chances remaining.'"
            msg2 = "(Guess with .rpgpuzzle XXXX)"
            input.conn.msg(input.chan, msg)
            input.conn.msg(input.chan, msg2)
            return
        elif self.choice == "riches":
            msg = "The " + self.thing + \
                " nods slowly. 'You have chosen the riddle; here are the rules. I will tell you the riddle, which has an answer one word long. "
            msg += "You have three chances to guess the answer. If it goes poorly, I may decide to give you a hint. Here is the riddle: "
            msg2 = "Now, begin your guess. You have three chances remaining.'"
            input.conn.msg(input.chan, msg)
            input.conn.msg(input.chan, self.riddle)
            input.conn.msg(input.chan, msg2)
            input.conn.msg(input.chan, "(Guess with .rpgpuzzle <word>)")
            return
        elif self.choice == "knowledge":
            msg = "The " + self.thing + \
                "'s face spreads in a predatory smile. 'As you wish. The Trial consists of three tests; if you succeed at all three, you will be rewarded."
            msg += " The first will begin as soon as you are ready.'"
            msg2 = "(Tell the " + self.thing + \
                " that you're ready with .rpgpuzzle)"
            input.conn.msg(input.chan, msg)
            input.conn.msg(input.chan, msg2)
            return
        else:
            self.failure(input, rpg)

    def failure(self, input, rpg):
        char = rpg.character
        input.conn.msg(input.chan, "The " + self.thing +
                       " stares at you impassively. 'You have been found wanting. How disappointing.' Then it vanishes, leaving no trace that this room of the dungeon was ever occupied.")
        if self.choice == "knowledge" and self.damage > 0:
            char.ouch(self.damage)
            msg = "The Trial was extremely taxing; you take " + \
                str(self.damage) + " damage"
            if char.currenthp <= 0:
                msg += "..."
            else:
                msg += ", and have " + \
                    str(char.currenthp) + " hit points remaining."
            input.conn.msg(input.chan, msg)
        rpg.destination("dungeon")
        return

    def success(self, input, rpg):
        char = rpg.character
        input.conn.msg(input.chan, "The " + self.thing +
                       " seems pleased. 'You have proven worthy, and now may receive your reward.' Then it vanishes, leaving no trace that this room of the dungeon was ever occupied.")
        msg = "You gain "
        if self.choice == "gold":
            msg += str(self.gold) + " gp!"
            input.conn.msg(input.chan, msg)
            char.defeat_enemy(0, {'gp': self.gold})
        if self.choice == "riches":
            typ = item_type(self.riches)
            msg += "a "
            if typ[0] == "ring":
                msg += "Ring of "
            msg += self.riches + "!"
            input.conn.msg(input.chan, msg)
            char.defeat_enemy(0, {typ[0]: self.riches})
        if self.choice == "knowledge":
            msg = str(self.knowledge) + " experience!"
            if char.exp + self.knowledge >= 10 * char.level:
                msg += " You have leveled up! Please choose a feat with .rpglvlup <feat> (if you need a reminder of what feats are available, use .rpghelp feats)."
            char.defeat_enemy(self.knowledge, {})
            input.conn.msg(input.chan, msg)
        rpg.destination("dungeon")
        return

    def trialofbeing(self, input, rpg):
        char = rpg.character
        sta = random.sample(
            ['Attack', 'Defense', 'Reflexes', 'Fortitude', 'Mind', 'Skill'], 3)
        tests = {
            'Attack':
            "All of a sudden, you find yourself inside a wooden box, 10 feet on a side. The walls begin to close in! You try to hack your way out...",
            'Defense':
            "Stalactites and stalagmites of various sizes start to elongate, sprouting from the floor, walls, and ceiling! You attempt to avoid being impaled...",
            'Reflexes':
            "The ground rumbles, twisting and gyrating in an earthquake! You try to keep your balance as chasms in the floor gape open...",
            'Fortitude':
            "An enormous python slithers out of thin air, coiling around you in an instant! You attempt to remain conscious as it constricts you...",
            'Mind':
            "You reel from a sudden psychic onslaught! You fight to keep your senses...",
            'Skill': "You are faced with a challenge that is both deadly and idiosyncratic! You try to defeat it using your ingenuity and cunning..."}
        win = {
            'Attack': "You break through the box before being crushed!",
            'Defense': "You protect yourself from evisceration!",
            'Reflexes': "You remain on your feet!",
            'Fortitude': "You fight off the impending blackness!", 'Mind': "You shake off the mental assault!", 'Skill': "You are up to the task!"}
        lose = {
            'Attack':
            "The contracting walls squeeze you to unconsciousness...",
            'Defense': "The stone spikes break through your defenses...",
            'Reflexes': "You fall into a chasm...", 'Fortitude': "You are forced to oblivion...", 'Mind': "Your mental defenses are overcome...", 'Skill': "You come up short..."}
        for i, s in enumerate(sta):
            input.conn.msg(input.chan, "The " + ("first", "second", "third")
                           [i] + " challenge begins. " + tests[s])
            res_char = random.choice([random.randint(0, char.stats[dstats[s]])
                                     for j in range(6)])
            res_test = random.choice([random.randint(0, self.tnum)
                                     for j in range(6)])
            if res_char < res_test:
                input.conn.msg(input.chan, lose[s])
                self.damage = res_test - res_char
                self.failure(input, rpg)
                return
            else:
                input.conn.msg(input.chan, win[s])
                self.knowledge += rpg.dungeonlevel
        self.success(input, rpg)

    def check_riddleguess(self, input, rpg, guess):
        self.riddleguess -= 1
        # check for a valid guess
        badguess = 0
        import string
        if len(guess.split()) > 1:
            badguess = 1
        for i in guess:
            if i not in string.letters:
                badguess = 2
                break
        if badguess:
            badmsg = ["your guess should be one word only.",
                      "what you said isn't even a word."][badguess - 1]
            input.conn.msg(input.chan, "The " + self.thing +
                           " frowns. 'I do not know why you would waste a guess on that... " + badmsg + "'")
            if self.riddleguess <= 0:
                self.failure(input, rpg)
            return
        # are they right?
        if guess.upper() == self.answer:
            self.success(input, rpg)
            return
        ng = len(self.answer)
        pl = "s" if self.riddleguess != 1 else ""
        msg = "You have guessed incorrectly, leaving you with " + \
            str(self.riddleguess) + " chance" + pl + " remaining. "
        if self.riddleguess == 2:
            msg += "Here is a hint to help you: the answer to the riddle is a single word with " + \
                str(ng) + " letters."
        input.conn.msg(input.chan, msg)
        if self.riddleguess <= 0:
            self.failure(input, rpg)
        return

    def check_numguess(self, input, rpg, guess):
        self.numguess -= 1
        # check for a valid guess
        badguess = False
        if len(guess) != 4:
            badguess = True
        for i in guess:
            try:
                j = int(i)
            except:
                badguess = True
        if badguess:
            input.conn.msg(input.chan, "The " + self.thing +
                           " frowns. 'I do not know why you would waste a guess on that.'")
            if self.numguess <= 0:
                self.failure(input, rpg)
            return
        copy_ans = [i for i in self.numcode]
        copy_guess = [i for i in guess]
        res = []
        # first pass: check for correct positions
        perc = 0
        for i in range(4):
            if copy_guess[i] == copy_ans[i]:
                res.append('rectus')
                copy_ans[i] = '*'
                copy_guess[i] = '*'
                perc += 2
        # did they get it right?
        if ''.join(copy_ans) == '****' or perc == 8:
            self.success(input, rpg)
            return
        # if not, are they done?
        if self.numguess <= 0:
            self.failure(input, rpg)
            return
        # if not, let's check for correct digits, incorrect positions
        for i in range(4):
            if copy_guess[i] != '*' and copy_guess[i] in copy_ans:
                res.append('proxime')
                perc += 1
        # fill out the rest with evil BWHAHA
        nres = len(res)
        for i in range(4 - nres):
            res.append('malum')
        # concatenate results
        hint = []
        nos = ['', 'singuli', 'bini', 'terni', 'quaterni']
        for i in ['rectus', 'proxime', 'malum']:
            num = res.count(i)
            if num > 0:
                print num
                hint.append(nos[num] + ' ' + i)
        hint = ', '.join(hint) + '.'
        perc = (perc + 1) / 2
        percmsg = (
            "The " + self.thing +
            " sighs. 'You are nearly as far from correct as it is possible to be. Perhaps this hint will help:",
            "The " + self.thing +
            " nods slowly. 'You have some small skill at this sort of thing, it would seem. A hint to aid your progress:",
            "The " + self.thing +
            " quirks an eyebrow. 'Perhaps you do not even need this hint, but I will provide it anyway:",
            "The " + self.thing + " smiles, showing a little too many teeth. 'I am impressed -- you are nearly there. Another hint:")
        if self.numguess > 1:
            nummsg = "You have " + \
                str(self.numguess) + " guesses remaining. Use them wisely."
        else:
            nummsg = "You have one guess remaining. Use it wisely."
        input.conn.msg(input.chan, " ".join([percmsg[perc], hint, nummsg]))
        return


class dCharacter:

    def __init__(self):
        self.name = ""
        self.level = 1
        self.hp = 1
        self.currenthp = 1
        self.sp = 1
        self.currentsp = 1
        self.race = ""
        self.clas = ""
        self.skill = []
        self.stats = [0, 0, 0, 0, 0, 0]
        self.feats = [""]
        self.nick = ""
        self.init = 0
        self.atk = [0, 0]
        self.dfn = 0
        self.gear = {"armor": {'name': '', 'rat': 0},
                     "weapon": {'name': '', 'rat': 0}, "ring": ""}
        self.loot = {"quest": '', "gp": 0, "items": []}
        self.exp = 0
        self.temp = {}
        self.tempturns = {}

    def chargen(self, nick, rac, cls, fets):
        rac = rac.lower()
        cls = cls.lower()
        self.nick = nick
        self.race = rac
        self.clas = cls
        self.name = namegen.web_namegen(5, 12, 2).replace('\n', ' ')
        self.exp = 0
        self.loot["gp"] = 0
        for i in range(0, 6):
            st = random.choice([random.randint(1, 4) for j in range(0, 6)])
            self.stats[i] = st + dclasses[cls]['stat'][i] + \
                draces[rac]['stat'][i]
        self.feats = fets
        for i in fets:
            if i.lower() == 'improvedinitiative':
                self.init += 2
            else:
                for j in dfeats.keys():
                    if i.lower() == j.lower():
                        self.stats[dfeats[j]] += 2
                        break
        self.hp = self.stats[3]
        self.sp = self.stats[5]
        self.currenthp = self.hp
        self.currentsp = self.sp
        self.gear['armor']['name'] = dgear['rarmor'][
            random.choice(dgear['rarmor'].keys())][0]
        self.gear['armor']['rat'] = 0
        self.gear['weapon']['name'] = dgear['rweapon'][
            random.choice(dgear['rweapon'].keys())][0]
        self.gear['weapon']['rat'] = 0
        self.gear['ring'] = ''
        self.atk = [self.gear['weapon']['rat'], self.stats[0]]
        self.dfn = [self.gear['armor']['rat'], self.stats[1]]
        self.skill = []
        self.skill.append(dclasses[self.clas]['skill'])

    def tellchar(self, input=None):
        input.conn.msg(input.chan, self.name + ' (Player: ' + self.nick + ')')
        input.conn.msg(input.chan, ' '.join(
            [self.race.capitalize(), self.clas.capitalize(), str(self.level)]))
        statstr = sum([[dst[i], str(self.stats[i])] for i in range(0, 6)], [])
        ft1 = collapse_list(self.feats, True)
        ft2 = []
        for f in ft1:
            if isinstance(f, list):
                f = f[0]
            cnt = self.feats.count(f)
            if cnt > 1:
                ft2.append(f + ' x' + str(cnt))
            else:
                ft2.append(f)
        ft2 = ', '.join(sorted(ft2))
        input.conn.msg(
            input.chan, '; '.join([' '.join(statstr), 'hp ' + str(self.currenthp) + '/' + str(self.hp),
                                   'sp ' + str(self.currentsp) + '/' + str(self.sp), 'exp ' + str(self.exp) + '/' + str(self.level * 10), ft2]))
        if not self.gear['armor']['name']:
            arm = 'Armor: None (0)'
        else:
            arm = 'Armor: ' + self.gear['armor']['name'] + \
                ' (' + str(self.gear['armor']['rat']) + ')'
        if not self.gear['weapon']['name']:
            wep = 'Weapon: None (-1)'
        else:
            wep = 'Weapon: ' + self.gear['weapon']['name'] + \
                ' (' + str(self.gear['weapon']['rat']) + ')'
        if not self.gear['ring']:
            ring = 'Ring: None'
        else:
            ring = 'Ring: ' + self.gear['ring']
        input.conn.msg(
            input.chan, '; '.join(['Skills: ' + ', '.join(self.skill), arm, wep, ring]))
        itm1 = collapse_list(self.loot['items'], True)
        fin = []
        if self.loot['quest']:
            fin = [self.loot['quest']]
        for f in itm1:
            if isinstance(f, list):
                f = f[0]
            cnt = self.loot['items'].count(f)
            if cnt > 1:
                out = f + ' x' + str(cnt)
            else:
                out = f
            if f.lower() in [i.lower() for i in dtreas['ring'].keys()]:
                fin.append("Ring of " + out)
            else:
                fin.append(out)
        if not fin:
            loot = 'None'
        else:
            loot = ', '.join(fin)
        input.conn.msg(input.chan, str(self.loot['gp']) + ' gp; loot: ' + loot)

    def levelup(self, fet):
        self.exp -= self.level * 10
        self.level += 1
        if isinstance(fet, list):
            fet = fet[0]
        if fet.lower() in 'improvedinitiative':
            self.init += 2
        else:
            for i in dfeats.keys():
                if i.lower() == fet.lower():
                    self.stats[dfeats[i]] += 2
                    self.feats.append(i)
        self.hp += random.choice([random.randint(max([1, self.stats[3] / 2]), 1 + self.stats[3])
                                 for j in range(0, 6)])
        self.sp += 2
        self.atk = [self.gear['weapon']['rat'], self.stats[0]]
        self.dfn = [self.gear['armor']['rat'], self.stats[1]]

    def sleep(self):
        self.temp = {}
        self.tempturns = {}
        self.currenthp = self.hp
        self.currentsp = self.sp

    def ouch(self, dmg):
        self.currenthp -= dmg

    def sammich(self, lvl):
        self.temp = {}
        self.tempturns = {}
        self.currenthp = self.hp if self.currenthp + \
            lvl > self.hp else self.currenthp + lvl
        self.currentsp = self.sp if self.currentsp + \
            lvl > self.sp else self.currentsp + lvl

    def equip(self, neweq):
        old = ''
        if neweq.get('armor', None):
            narm = neweq['armor']
            nrat = drating(item_type(narm), narm)
            if self.gear['armor']['name']:
                arat = self.gear['armor']['rat']
                self.loot['items'].append(self.gear['armor']['name'])
                old = self.gear['armor']['name']
            else:
                arat = 0
            self.gear['armor']['name'] = narm
            self.gear['armor']['rat'] = nrat
            self.loot['items'].remove(narm)
        elif neweq.get('weapon', None):
            nwep = neweq['weapon']
            nrat = drating(item_type(nwep), nwep)
            if self.gear['weapon']['name']:
                wrat = self.gear['weapon']['rat']
                self.loot['items'].append(self.gear['weapon']['name'])
                old = self.gear['weapon']['name']
            else:
                wrat = 0
            self.gear['weapon']['name'] = nwep
            self.gear['weapon']['rat'] = nrat
            self.loot['items'].remove(nwep)
        elif neweq.get('ring', None):
            nring = neweq['ring']
            if self.gear['ring']:
                self.skill.remove(dtreas['ring'][self.gear['ring']])
                self.loot['items'].append(self.gear['ring'])
                old = self.gear['ring']
            self.skill.append(dtreas['ring'][nring])
            self.gear['ring'] = nring
            self.loot['items'].remove(nring)
        self.atk = [self.gear['weapon']['rat'], self.stats[0]]
        self.dfn = [self.gear['armor']['rat'], self.stats[1]]
        if old:
            return old
        return

    def complete_quest(self, exp, gp):
        self.loot['quest'] = ''
        self.exp += exp
        self.loot['gp'] += gp

    def sell_loot(self, sell, num=1):
        if isinstance(sell, list):
            sell = sell[0]
        lowitems = [x.lower() for x in self.loot['items']]
        if sell.lower() not in lowitems:
            return False
        val = item_worth(sell) / 2
        if val == 0:
            val = 1
        out = []
        for j in sorted(self.loot['items']):
            if sell.lower() == j.lower() and num > 0:
                self.loot['gp'] += val
                num -= 1
            else:
                out.append(j)
        self.loot['items'] = out
        return True

    def buy_loot(self, buy, gp):
        self.loot['items'].append(buy.lower().capitalize())
        self.loot['gp'] -= gp

    def defeat_enemy(self, lvl, loot):
        self.temp = {}
        self.tempturns = {}
        self.exp += lvl
        for i in loot.keys():
            if i == 'gp':
                self.loot['gp'] += loot[i]
            elif i == 'quest' and not self.loot['quest']:
                self.loot['quest'] = loot['quest']
            elif loot[i]:
                self.loot['items'].append(loot[i])


class dMonster:

    def __init__(self):
        self.name = ''
        self.level = 0
        self.hp = 0
        self.currenthp = 0
        self.sp = 0
        self.currentsp = 0
        self.stats = [0, 0, 0, 0, 0, 0]
        self.treasure = {'weapon': '', 'armor': '', 'ring': '', 'gp': 0}
        self.skill = ''
        self.temp = {}
        self.tempturns = {}
        self.atk = [0, self.stats[0]]
        self.dfn = [0, self.stats[1]]
        self.skillcounter = 1

    def gen(self, lvl):
        if lvl >= 10:
            self.dragongen(lvl)
        else:
            self.level = lvl
            self.name = random.choice(dmonst[lvl].keys())
            tmp = dmonst[lvl][self.name]
            for i in range(0, 6):
                st = random.choice([random.randint(1, 6) for j in range(0, 6)])
                self.stats[i] = st + tmp['stat'][i]
            self.skill = tmp['skill']
            for i in range(0, lvl):
                self.hp += random.choice([random.randint(max([1, self.stats[3] / 2]), self.stats[3])
                                         for j in range(0, 6)])
            self.currenthp = self.hp
            self.sp = random.choice([random.randint(1, self.stats[5])
                                    for j in range(0, 6)]) + 2 * (lvl - 1)
            self.currentsp = self.sp
            self.treasure = treasuregen(lvl)
            self.atk = [0, self.stats[0]]
            self.dfn = [0, self.stats[1]]

    def dragongen(self, lvl):
        self.level = lvl
        color = random.choice([random.choice(dskill.keys())
                              for i in range(0, 6)])
        self.name = namegen.dragon_namegen(
            2, 6)[0] + ' the ' + color + ' Dragon'
        for i in range(0, 6):
            st = random.choice([random.randint(1, 6) for j in range(0, 6)])
            self.stats[i] = st + lvl - 5
        self.skill = dskill[color]
        for i in range(0, lvl):
            self.hp += random.choice([random.randint(1, self.stats[3])
                                     for j in range(0, 6)])
        self.currenthp = self.hp
        self.sp = random.choice([random.randint(1, self.stats[5])
                                for j in range(0, 6)]) + 2 * (lvl - 1)
        self.currentsp = self.sp
        self.treasure = treasuregen(lvl)
        self.atk = [lvl / 3, self.stats[0]]
        self.dfn = [lvl / 3, self.stats[1]]


class dQuest(dMonster):

    def __init__(self):
        dMonster.__init__(self)
        self.desc = ''
        self.arty = []

    def gen(self, lvl):
        self.level = lvl
        self.name = namegen.simple_namegen(2, 5).capitalize()
        self.desc = namegen.monster_gen()
        for i in range(0, 6):
            st = random.choice([random.randint(1, 6) for j in range(0, 6)])
            self.stats[i] = st + lvl
        art = namegen.artygen().split(':')
        self.treasure['quest'] = art[0].strip()
        self.arty = [a.strip() for a in art]
        self.skill = 'Cure'
        for i in range(0, lvl):
            self.currenthp += random.choice([random.randint(max([1, self.stats[3] / 2]), self.stats[3])
                                            for j in range(0, 6)])
        self.currentsp = random.choice([random.randint(1, self.stats[5])
                                       for j in range(0, 6)]) + 2 * (lvl - 1)
        self.hp = self.currenthp
        self.sp = self.currentsp
        self.atk = [lvl / 2, self.stats[0]]
        self.dfn = [lvl / 2, self.stats[1]]


class Combat:

    def __init__(self, lvl, char, enemy):
        if not enemy:
            self.enemy = dMonster()
            self.enemy.gen(lvl)
        else:
            self.enemy = enemy
        self.turn = -1
        self.charname = char.name
        cint = 1 + \
            char.init if char.stats[2] < 2 else random.choice(
                [random.randint(1, char.stats[2]) + char.init for j in range(0, 6)])
        mint = 1 if self.enemy.stats[2] < 2 else random.choice(
            [random.randint(1, self.enemy.stats[2]) for j in range(0, 6)])
        self.turnorder = ['monster', 'player']
        if cint > mint:
            self.turnorder = ['player', 'monster']
        elif cint == mint:
            if char.stats[2] > self.enemy.stats[2]:
                self.turnorder = ['player', 'monster']
            elif char.stats[2] == self.enemy.stats[2]:
                if 'ImprovedInititiative' in char.feats:
                    self.turnorder = ['player', 'monster']
                elif random.randint(0, 1):
                    self.turnorder = ['player', 'monster']

    def advance_turn(self, input, rpg, char):
        self.turn += 1
        whos = self.turnorder[self.turn % 2]
        self.enemy.skillcounter -= 1
        for i in char.temp.keys():
            char.tempturns[i] -= 1
            if char.tempturns[i] < 0:
                del char.tempturns[i], char.temp[i]
                if char.currenthp <= 0:
                    rpg.death(input, char)
                    return
        for i in self.enemy.temp.keys():
            self.enemy.tempturns[i] -= 1
            if self.enemy.tempturns[i] < 0:
                del self.enemy.tempturns[i], self.enemy.temp[i]
                if self.enemy.currenthp <= 0:
                    rpg.death(input, self.enemy)
                    return
        if whos == 'monster':
            if self.enemy.currentsp > 0 and ((self.enemy.skill == 'Petrify' and self.enemy.skillcounter < -2) or self.enemy.skillcounter < 0):
                input.conn.msg(input.chan, "The enemy uses " +
                               self.enemy.skill + "!")
                rpg.use_skill(input, self.enemy.skill,
                              self.enemy, rpg.character)
                self.enemy.skillcounter = 1 if self.enemy.skill != 'Flee' else - \
                    1
            else:
                input.conn.msg(input.chan,
                               "It tries to cause you bodily harm!")
                rpg.attack_enemy(input, self.enemy, rpg.character)


class Rpg:

    def __init__(self):
        self.character = dCharacter()
        self.player_nick = ""
        self.game_channel = ""
        self.questlevel = 0
        self.dungeonlevel = 1
        self.maxdgnlevel = 1
        self.quest = {}
        self.queststatus = "inactive"
        self.store = ['Dagger']
        self.chardeath = False
        self.whereareyou = ""
        self.shrinexp = 0
        self.shrinegp = 0

    def validate_player(self, input):
        if input.nick.lower() != self.player_nick.lower():
            input.conn.msg(input.chan, "Sorry, " + input.nick +
                           ", you're not the active player right now.")
            return False
        if input.chan.lower() != self.game_channel.lower():
            input.conn.msg(input.chan, "Sorry, " + input.nick +
                           ", that command wasn't in the right channel.")
            return False
        return True

    def initialize_channel(self, input):
        if not self.player_nick:
            try:
                self.player_nick = input.nick
                self.game_channel = "#RPG_" + input.nick.strip()
                input.conn.send('JOIN ' + self.game_channel)
                input.conn.send('TOPIC {} :{}'.format(
                    self.game_channel, ".rpgtown(dungeon,quest,rest,shop)|.rpgdungeon(backtrack,explore,return)|.rpgturn(attack,equip,flee,skill)|.rpghelp|.rpgsheet|.rpgcg|.rgpinit|.rpglvlup|.rpgbuy/.rpgsell"))
                #input.conn.msg('ChanServ','SET '+self.game_channel+' OWNERMODE ON')
                #input.conn.msg('ChanServ','SET '+self.game_channel+' PROTECTMODE ON')
                #input.conn.msg('ChanServ','SYNC '+self.game_channel)
                #input.conn.send('MODE ' + self.game_channel+' +m')
                #input.conn.msg('ChanServ','VOP '+self.game_channel+' ADD '+input.nick)
                input.conn.msg(input.chan, 'OK, ' + input.nick + ', your game is ready in ' + self.game_channel +
                               ' -- when you get there, type ".rpginit" to begin. If anyone else would like to watch, join the channel, but you won\'t be able to give any commands.')
                input.conn.msg(
                    input.chan, 'It\'s possible bears will make this game multiplayer in the future, though.')
                return True
            except:
                input.conn.msg(input.chan, 'Sorry, ' + input.nick +
                               ', there was an error in initializing your game session.')
                return False
        elif not self.validate_player(input):
            return False
        else:
            return True

    def atk_roll(self, atk, dfn, atkadj=0, defadj=0):
        if atk[1] <= atk[0]:
            atk_res = atk[0] + atkadj
        else:
            atk_res = random.choice([random.randint(atk[0], atk[1])
                                    for i in range(0, 6)]) + atkadj
        if dfn[1] <= dfn[0]:
            dfn_res = dfn[0] + defadj
        else:
            dfn_res = random.choice([random.randint(dfn[0], dfn[1])
                                    for i in range(0, 6)]) + defadj
        return atk_res - dfn_res

    def be_hit(self, input, target, dmg):
        target.currenthp -= dmg
        if target == self.character:
            input.conn.msg(input.chan, "Ouch! You're bleeding, maybe a lot. You take " +
                           str(dmg) + " damage, and have " + str(target.currenthp) + " hit points remaining.")
        else:
            input.conn.msg(
                input.chan, "A hit! A very palpable hit! You deal " + str(dmg) + " damage.")
        if target.currenthp <= 0:
            self.death(input, target)
            return True

    def win_combat(self, input=None):
        self.character.defeat_enemy(
            self.combat.enemy.level, self.combat.enemy.treasure)
        exp = self.combat.enemy.level
        msg = 'You receive ' + str(exp) + ' experience.'
        limit = self.character.level * 10
        if self.character.exp >= limit:
            msg += ' You have leveled up! Please choose a feat with .rpglvlup <feat> (if you need a reminder of what feats are available, use .rpghelp feats).'
        input.conn.msg(input.chan, msg)
        tr = self.combat.enemy.treasure
        msg = "In the monster's pockets, you find: "
        fin = []
        for i in tr.keys():
            if tr[i]:
                if i == 'gp':
                    fin.append(str(tr[i]) + " gp")
                elif i == 'ring':
                    fin.append("a Ring of " + tr[i])
                elif i == 'quest':
                    fin.append(tr[i])
                    self.queststatus = "complete"
                else:
                    fin.append("a " + tr[i])
        if not fin:
            fin = "Nothing!"
        else:
            fin = ', '.join(fin) + '.'
        input.conn.msg(input.chan, msg + fin)
        self.whereareyou = "dungeon"
        self.combat = None

    def death(self, input, target):
        if target == self.character:
            input.conn.msg(input.chan, 'Sorry, ' + self.character.nick +
                           ', you have died. You can use the command ".rpgload" to load from your last save, ".rpgquit" to quit, or ".rpgg" to make a new character.')
            self.temp = {}
            self.tempturns = {}
            self.chardeath = True
            self.combat = None
            return
        if target == self.combat.enemy:
            input.conn.msg(input.chan, 'You have defeated the ' +
                           self.combat.enemy.name + '!')
            self.win_combat(input)
            return

    def temp_bonus(self, input, target, stat, bon, turns):
        for i in stat:
            if target.temp.get(i, False):
                sign = -1 if bon < 0 else 1
                bon = sign * max([abs(target.temp[i]), abs(bon)])
            target.temp[i] = bon
            target.tempturns[i] = turns

    def new_char(self):
        self.chardeath = 0
        self.questlevel = 0
        self.dungeonlevel = 1
        self.maxdgnlevel = 1
        self.quest = {}
        self.queststatus = "inactive"
        self.store = ['Dagger']

    def attack_enemy(self, input, user, target):
        hit = self.atk_roll(user.atk, target.dfn, user.temp.get(
            "Attack", 0), target.temp.get("Defense", 0))
        if hit > 0:
            if not self.be_hit(input, target, hit):
                self.combat.advance_turn(input, self, self.character)
        else:
            input.conn.msg(input.chan, "The attack is unsuccessful.")
            self.combat.advance_turn(input, self, self.character)

    def use_skill(self, input, skill, user, target):
        if skill not in user.skill:
            return 0
        if user.currentsp == 0:
            return 1
        user.currentsp -= 1

        if skill == 'Smite':  # attack with Atk+Skill
            tmp_atk = user.atk
            tmp_atk[1] += random.randint(0, user.stats[5])
            hit = self.atk_roll(
                tmp_atk, target.dfn, user.temp.get("Attack", 0), target.temp.get("Defense", 0))
            if hit > 0:
                if not self.be_hit(input, target, hit):
                    self.combat.advance_turn(input, self, self.character)
                    return 2
            else:
                input.conn.msg(input.chan, "The Smite failed to connect.")
                self.combat.advance_turn(input, self, self.character)

        if skill == 'Cure':  # regain hp
            cure = random.randint(
                1, user.stats[5] + user.temp.get("Skill", 0)) + user.level
            if user.currenthp + cure > user.hp:
                user.currenthp = user.hp
            else:
                user.currenthp += cure
            cur = "You are " if user == self.character else "The monster is "
            input.conn.msg(input.chan, cur + "cured for " +
                           str(cure) + " hp! An attack follows.")
            self.attack_enemy(input, user, target)

        if skill == 'Charm':  # chance to end encounter, vs Mind
            hit1 = self.atk_roll([0, user.stats[5]], [0, target.stats[4]], user.temp.get(
                "Skill", 0), target.temp.get("Mind", 0))
            hit2 = self.atk_roll([0, user.stats[5]], [0, target.stats[4]], user.temp.get(
                "Skill", 0), target.temp.get("Mind", 0))
            hit3 = self.atk_roll([0, user.stats[5]], [0, target.stats[4]], user.temp.get(
                "Skill", 0), target.temp.get("Mind", 0))
            if hit1 > 0 and hit2 > 0 and hit3 > 0:
                self.death(input, target)
                return 2
            else:
                input.conn.msg(input.chan, "The Charm failed.")
                self.combat.advance_turn(input, self, self.character)

        if skill == 'Entangle':  # debuff targets atk, def for 2 turns, vs Ref
            hit = self.atk_roll([0, user.stats[5]], [0, target.stats[2]],
                                user.temp.get("Skill", 0), target.temp.get("Reflex", 0))
            if hit > 0:
                cur = "The monster is " if user == self.character else "You are "
                input.conn.msg(input.chan, cur + "entangled!")
                self.temp_bonus(input, target, ['Attack', 'Defense'], -hit, 4)
            else:
                input.conn.msg(input.chan, "The Entangle failed.")
            self.combat.advance_turn(input, self, self.character)

        if skill == 'Trip':  # deal dmg and target loses turn, vs Atk
            hit = self.atk_roll(
                user.atk, target.atk, user.temp.get("Attack", 0), target.temp.get("Attack", 0))
            if hit > 0:
                hit = max([hit / 2, 1])
                if not self.be_hit(input, target, hit):
                    cur = "The monster is " if user == self.character else "You are "
                    input.conn.msg(input.chan, cur + "tripped!")
                    deb = max([0, random.choice([random.randint(0, user.stats[5])
                              for i in range(0, 6)]) + user.temp.get("Skill", 0)])
                    self.temp_bonus(input, target, ["Attack"], deb, 4)
                    self.combat.advance_turn(input, self, self.character)
                    return 2
            else:
                input.conn.msg(input.chan, "The Trip failed.")
                self.combat.advance_turn(input, self, self.character)

        if skill == 'Missile':  # deal dmg vs Ref
            hit = self.atk_roll([0, user.stats[5]], [0, target.stats[2]],
                                user.temp.get("Skill", 0), target.temp.get("Reflex", 0))
            if hit > 0:
                if not self.be_hit(input, target, hit):
                    self.combat.advance_turn(input, self, self.character)
                    return 2
            else:
                input.conn.msg(input.chan, "The Missile failed to connect.")
                self.combat.advance_turn(input, self, self.character)

        if skill == 'Doublestrike':  # two attacks at smaller bonus
            hit1 = self.atk_roll(user.atk, target.dfn, user.temp.get(
                "Attack", 0) - 2, target.temp.get("Defense", 0))
            hit2 = self.atk_roll(user.atk, target.dfn, user.temp.get(
                "Attack", 0) - 2, target.temp.get("Defense", 0))
            if hit1 < 0:
                hit1 = 0
            if hit2 < 0:
                hit2 = 0
            hit = hit1 + hit2
            if hit > 0:
                if not self.be_hit(input, target, hit):
                    self.combat.advance_turn(input, self, self.character)
                    return 2
            else:
                input.conn.msg(input.chan,
                               "The Doublestrike failed to connect.")
                self.combat.advance_turn(input, self, self.character)

        if skill == 'Backstab':  # Skill vs Fort for double dmg on attack
            check = self.atk_roll([0, user.stats[5]], [0, target.stats[3]], user.temp.get(
                "Skill", 0), target.temp.get("Fortitude", 0))
            hit = self.atk_roll(user.atk, target.dfn, user.temp.get(
                "Attack", 0), target.temp.get("Defense", 0))
            if hit > 0:
                if check > 0:
                    hit *= 2
                if not self.be_hit(input, target, hit):
                    self.combat.advance_turn(input, self, self.character)
                    return 2
            else:
                input.conn.msg(input.chan, "The Backstab failed to connect.")
                self.combat.advance_turn(input, self, self.character)

        if skill == 'Rage':  # attack with +atk, -def
            hit = self.atk_roll(user.atk, target.dfn, user.temp.get(
                "Attack", 0) + user.stats[5], target.temp.get("Defense", 0))
            self.temp_bonus(input, user, ["Defense"], -2, 4)
            if hit > 0:
                if not self.be_hit(input, target, hit):
                    self.combat.advance_turn(input, self, self.character)
                    return 2
            else:
                input.conn.msg(input.chan,
                               "The Rage-fueled attack failed to connect.")
                self.combat.advance_turn(input, self, self.character)

        if skill == 'Evade':  # gain +def
            self.temp_bonus(input, user, ('Defense'), user.stats[5], 4)
            cur = "You are " if user == self.character else "The monster is "
            input.conn.msg(input.chan, cur + "feeling much more evasive!")
            self.combat.advance_turn(input, self, self.character)

        if skill == 'Flee':  # escape from combat
            cur = "You are " if user == self.character else "The monster is "
            input.conn.msg(input.chan, cur + "running away!")
            self.runaway(input, user, 1.)
            self.whereareyou = "dungeon"
            self.combat = None
            return 2

        if skill == 'Poison':  # Auto-dmg if not at max hp
            if target.currenthp < target.hp:
                if not self.be_hit(input, target, user.stats[5]):
                    self.combat.advance_turn(input, self, self.character)
                    return 2
            else:
                cur = " the monster." if user == self.character else " you."
                input.conn.msg(input.chan, "The Poison failed to affect" + cur)
                self.combat.advance_turn(input, self, self.character)

        if skill == 'Fear':  # Debuff vs Mind
            hit = self.atk_roll([0, user.stats[5]], [0, target.stats[4]],
                                user.temp.get("Skill", 0), target.temp.get("Mind", 0))
            if hit > 0:
                amt = hit / 2
                if amt == 0:
                    amt = 1
                cur = "The monster is " if user == self.character else "You are "
                input.conn.msg(input.chan, cur + "frightened!")
                self.temp_bonus(input, target,
                                ['Attack', 'Defense', 'Skill'], -amt, 3)
            else:
                cur = " the monster." if user == self.character else " you."
                input.conn.msg(input.chan, "The Fear failed to affect" + cur)
            self.combat.advance_turn(input, self, self.character)

        if skill == 'Petrify':  # chance to end encounter, vs Fort
            hit1 = self.atk_roll([0, user.stats[5]], [0, target.stats[3]], user.temp.get(
                "Skill", 0), target.temp.get("Fortitude", 0))
            hit2 = self.atk_roll([0, user.stats[5]], [0, target.stats[3]], user.temp.get(
                "Skill", 0), target.temp.get("Fortitude", 0))
            hit3 = self.atk_roll([0, user.stats[5]], [0, target.stats[3]], user.temp.get(
                "Skill", 0), target.temp.get("Fortitude", 0))
            if hit1 > 0 and hit2 > 0 and hit3 > 0:
                self.death(input, target)
                return 2
            else:
                input.conn.msg(input.chan, "The Petrify failed.")
                self.combat.advance_turn(input, self, self.character)

        return 2

    def runaway(self, input, who, ch=0.5):
        if random.random() < ch:
            if who == self.character:
                input.conn.msg(
                    input.chan, "You successfully exercise your valor, vis a vis discretion.")
            else:
                input.conn.msg(
                    input.chan, "Your enemy turns tail and books it back into the dungeon.")
            return True
        else:
            if who == self.character:
                input.conn.msg(input.chan,
                               "You try to run, but the enemy boxes you in.")
            else:
                input.conn.msg(input.chan,
                               "You prevent your enemy from skedaddling.")
            return False

    def check_backtrack(self):
        chk = self.character.stats[4] - self.dungeonlevel
        if chk < 0:
            cut = float(3 - chk) / float(6 - 6 * chk)
        else:
            cut = float(3 + 5 * chk) / float(6 + 6 * chk)
        bak = True if random.random() < cut else False
        return bak

    def init_quest(self, level):
        self.quest = dQuest()
        self.quest.gen(level)

    def addshopitem(self):
        tr = treasuregen(self.questlevel)
        for i in tr.keys():
            if tr[i]:
                if i != 'gp' and tr[i] not in self.store:
                    self.store.append(tr[i])

    def telltown(self, input, start=False):
        msg = "You begin in the town square. " if start else ""
        msg += "To the East is your humble abode and warm bed; to the North, the General Store where various and sundry goods may be purchased; "
        msg += "to the West, the Questhall where the mayor makes his office; "
        msg += "to the Northwest, the local Shrine to the Unknowable Gods; and to the South lie the gates of the city, leading out to the Dungeon."
        input.conn.msg(input.chan, msg)

    def questhall(self, input=None):
        if self.queststatus == "active":
            input.conn.msg(input.chan, "As you enter the Questhall, Mayor Percival looks at you expectantly. 'Did you collect the item and defeat the monster? No? Well, then, get back out there! I suggest you try Dungeon level " +
                           str(self.questlevel) + ".")
            return
        self.questlevel += 1
        self.quest = dQuest()
        self.quest.gen(self.questlevel)
        if self.queststatus == "inactive":
            msg1 = "In the Questhall, Mayor Percival frets behind his desk. '" + self.character.name + \
                "! Just the person I was looking for. There's... something I need you to do."
            msg2 = " See, there are rumors of a horrible creature, called " + \
                self.quest.name + ", roaming the dungeon."
            input.conn.msg(input.chan, msg1 + msg2)
            input.conn.msg(input.chan, self.quest.desc)
            msg1 = "This monstrosity draws its power from " + \
                self.quest.arty[0] + ", " + \
                self.quest.arty[
                    1].lower() + " I need you to go into the dungeon, kill that beast, and bring back the artifact so my advisors can destroy it."
            msg2 = " The townspeople will be very grateful, and you'll receive a substantial reward! Now, get out of here and let me finish my paperwork.'"
            input.conn.msg(input.chan, msg1 + msg2)
            self.queststatus = "active"
        elif self.queststatus == "complete":
            self.queststatus = "active"
            input.conn.msg(
                input.chan, "Mayor Percival looks up excitedly. 'You have it! Well, thank my lucky stars. You're a True hero, " + self.character.name + "!'")
            exp = 5 * (self.questlevel - 1)
            gp = int(random.random() * 2 + 1) * exp
            msg = "You gain " + \
                str(exp) + " experience and " + str(gp) + " gp."
            self.character.complete_quest(exp, gp)
            limit = self.character.level * 10
            if self.character.exp + exp > limit:
                msg += ' You have leveled up! Please choose a feat with .rpglvlup <feat> (if you need a reminder of what feats are available, use .rpghelp feats).'
            input.conn.msg(input.chan, msg)
            self.addshopitem()
            msg1 = "Percival clears his throat hesitantly. 'Since I have you here, there... have been rumors of another problem in the dungeon. "
            msg2 = self.quest.name + " is its name. " + self.quest.desc
            input.conn.msg(input.chan, msg1 + msg2)
            input.conn.msg(input.chan, "The source of its power is " + self.quest.arty[0] + ", " + self.quest.arty[1] +
                           " Will you take this quest, same terms as last time (adjusting for inflation)? Yes? Wonderful! Now get out.'")

    def destination(self, loc):
        self.whereareyou = loc

    def godownstairs(self, input=None):
        if self.whereareyou != "stairs":
            print "NO STAIRS BLARGH"
            return
        self.whereareyou = "start"
        self.dungeonlevel += 1
        if self.dungeonlevel > self.maxdgnlevel:
            self.maxdgnlevel = self.dungeonlevel
        input.conn.msg(
            input.chan, "You head down the stairs to level " + str(self.dungeonlevel))
        return

    def explore(self, input=None):
        room = random.choice([random.randint(1, 20) for i in range(0, 6)])
        if room <= 2:
            input.conn.msg(
                input.chan, "You find a flight of stairs, leading down! Explore again to go down to the next level, or backtrack to stay on this one.")
            self.whereareyou = "stairs"
            return
        elif room > 2 and room <= 5:
            msg = "You found a chest! "
            tr = treasuregen(self.dungeonlevel)
            self.character.defeat_enemy(0, tr)
            fin = []
            for i in tr.keys():
                if tr[i]:
                    if i == 'gp':
                        fin.append(str(tr[i]) + " gp")
                    elif i == 'ring':
                        fin.append("a Ring of " + tr[i])
                    else:
                        fin.append("a " + tr[i])
            if not fin:
                msg += "Sadly, it was empty."
            else:
                msg += 'Inside, you find ' + ', '.join(fin) + '.'
            input.conn.msg(input.chan, msg)
            return
        elif room > 5 and room <= 8:
            dl = self.dungeonlevel
            if 'milo' in self.player_nick.lower():
                foo = 'a taco-like'
            else:
                #from xkcd import sandgen
                foo = "a delicious"  # sandgen()
            input.conn.msg(input.chan, "The room echoes with a hollow emptiness, and you reflect on the vagaries of living life alone... Then you eat " +
                           foo + " sandwich, and get ready to kill more things.")
            input.conn.msg(input.chan, "You regain " + str(dl) + " hp and sp!")
            self.character.sammich(dl)
        elif room > 8 and room <= 10:
            self.whereareyou = "puzzle"
            self.puzzle = dPuzzle(self.dungeonlevel)
            self.puzzle.puzzlemsg(input)
        elif room > 10:
            msg = "You've stumbled on an enemy! It seems to be... "
            chk = self.maxdgnlevel - self.questlevel
            cut = float(1 + chk) / float(10 + 2 * chk)
            if self.dungeonlevel == self.questlevel and self.quest and self.queststatus == "active" and random.random() < cut:
                self.combat = Combat(
                    self.dungeonlevel, self.character, self.quest)
                msg += self.quest.name + '!'
            else:
                self.combat = Combat(self.dungeonlevel, self.character, None)
                if self.dungeonlevel >= 10:
                    msg += self.combat.enemy.name + '!'
                else:
                    msg += 'a ' + self.combat.enemy.name + '!'
            if self.combat.turnorder[0] == 'player':
                msg += ' You get the jump on it.'
            else:
                msg += ' It gets the jump on you.'
            input.conn.msg(input.chan, msg)
            self.whereareyou = "combat"
            self.combat.advance_turn(input, self, self.character)

    def display_itemlist(self, itemlist, sell=False):
        itm1 = collapse_list(itemlist, True)
        fin = []
        for j, f in enumerate(itm1):
            price = item_worth(f)
            if sell:
                price = max([price / 2, 1])
            if isinstance(f, list):
                f = f[0]
            cnt = itemlist.count(f)
            if cnt > 1:
                out = f + ' x' + str(cnt)
            else:
                out = f
            if f.lower() in [i.lower() for i in dtreas['ring'].keys()]:
                fin.append(str(j + 1) + ". Ring of " +
                           out + " (" + str(price) + ")")
            else:
                fin.append(str(j + 1) + ". " + out + " (" + str(price) + ")")
        return fin

    def visit_shop(self, input=None):
        self.whereareyou = "shop"
        msg1 = "The shopkeep greets you cheerfully. 'Welcome, hero! What can I do for you?' His current inventory is: "
        fin = self.display_itemlist(self.store)
        if not fin:
            msg1 += "Nothing!"
        else:
            msg1 += " ".join(fin) + "."
        input.conn.msg(input.chan, msg1)
        msg2 = "Your current loot bag contains " + \
            str(self.character.loot['gp']) + " gp, and: "
        fin = self.display_itemlist(self.character.loot['items'], True)
        if not fin:
            msg2 += "Nothing!"
        else:
            msg2 += " ".join(fin) + "."
        input.conn.msg(input.chan, msg2)
        input.conn.msg(
            input.chan, "Use .rpgbuy and .rpgsell for transactions, or .rpgtown to leave the shop.")

    def visit_shrine(self, input=None):
        self.whereareyou = "shrine"
        self.gods = namegen.godgen(2)
        msg = "The Shrine is mostly deserted at this time of day. Two of the altars catch your eye: one to " + \
            self.gods[0] + \
            ", which offers Enlightenment on a sliding tithe scale; "
        msg += "and one to " + \
            self.gods[1] + \
            ", which promises Materialism for a single lump sum of 30,000gp."
        msg2 = "(Use .rpgshrine <choice> <offering> to make an offering; choice 1 is Enlightenment, choice 2 is Materialism.)"
        input.conn.msg(input.chan, msg)
        input.conn.msg(input.chan, msg2)

    def offering(self, input, choice, amt):
        if amt < 0:
            input.conn.msg(input.chan, "You can't take money out of the offering bowl, not without offending " +
                           self.gods[int(choice) - 1] + ", which you do NOT want to do.")
            return
        elif amt == 0:
            input.conn.msg(input.chan, "Nothing ventured, nothing gained.")
            return
        elif amt > self.character.loot['gp']:
            input.conn.msg(
                input.chan, "You don't have enough gold for that, man. Go back to the dungeon and make some scratch! (Or at least, put less in the offering bowl.)")
            return
        if str(choice) == '1':
            try:
                self.shrinegp += amt
            except AttributeError:
                self.shrinegp = amt
            from math import sqrt
            newexp = int((1. + sqrt(1. + 8. * float(self.shrinegp))) / 4.)
            try:
                net = newexp - self.shrinexp
            except AttributeError:
                net = newexp
            self.shrinexp = newexp
            input.conn.msg(input.chan, "The bounds of your mind are expanded by a moment of attention from " +
                           self.gods[0] + "; this may not actually be a good thing, but at least you gain " + str(net) + " experience.")
            self.character.defeat_enemy(net, {'gp': -amt})
            if self.character.exp >= self.character.level * 10:
                input.conn.msg(
                    input.chan, "You have leveled up! Please choose a feat with .rpglvlup <feat> (if you need a reminder of what feats are available, use .rpghelp feats).")
            return
        elif str(choice) == '2':
            if amt < 30000:
                input.conn.msg(
                    input.chan, "Nothing happens except for a feeling of insufficient funds... you scoop the gold back out of the offering bowl before anyone sees you, cheapskate.")
                return
            t = random.choice([random.randint(0, 2) for i in range(6)])
            typ1 = ["ring", "rarmor", "rweapon"][t]
            t2 = ["ring", "armor", "weapon"][t]
            if typ1 == "ring":
                tr = random.choice([random.choice(dtreas['ring'].keys())
                                   for i in range(6)])
            else:
                typ2 = random.choice([random.choice(dtreas[typ1].keys())
                                     for i in range(6)])
                rat = random.choice([random.randint(0, 8) for i in range(6)])
                if rat == 0:
                    tr = dgear[typ1][typ2][0]
                else:
                    mrat = random.choice([random.randint(max([rat - 5, 0]), min([3, rat]))
                                         for i in range(6)]) if rat < 8 else 3
                    irat = rat - mrat
                    tr = '' if mrat == 0 else dtreas[typ1][typ2][mrat] + ' '
                    tr += dgear[typ1][typ2][irat]
            self.character.defeat_enemy(0, {'gp': -amt, t2: tr})
            msg = "The gold disappears from the offering bowl"
            if amt > 30000:
                msg += " (with a thank you very much for the extra donation)"
            msg += ", and you discover a "
            if t2 == "ring":
                msg += "Ring of "
            msg += tr + " in your lootbag!"
            input.conn.msg(input.chan, msg)
            return

    def save(self):
        d = shelve.open(os.path.expanduser('persist/rpgsaves.db'))
        d[self.player_nick] = self
        d.close()


rpgs = {}


@hook.command('rpg', autohelp=False)
def dnd(inp, input=None, bot=None):
    ".rpg - begin an rpg in #RPG_<your nick> (single player for now)"
    input.nick = str(input.nick)
    global rpgs
    if input.nick in rpgs:
        if input.nick == rpgs[input.nick].game_channel:
            input.conn.msg(input.chan, "You're already here...?")
            return
        input.conn.msg(input.chan, "You realize you're already playing, right? Or... maybe you didn't quit when you were done? Well either way, your channel is " +
                       rpgs[input.nick].game_channel + ".")
        return
    rpgs[input.nick] = Rpg()
    rpgs[input.nick].initialize_channel(input)
    rpgs[input.nick].save()


@hook.command(autohelp=False)
def rpginit(inp, input=None):
    input.nick = str(input.nick)
    global rpgs
    rpg = rpgs.get(input.nick, None)
    if not rpg:
        return
    if not rpg.validate_player(input):
        return
    if rpg.character.name:
        input.conn.msg(input.chan,
                       "Your game is already initialized, what's the problem?")
        return
    input.conn.msg(input.chan, "Welcome to Percival's Quest! This is a solo (as of yet) random dungeoncrawl rpg written for IRC. The current player is " + input.nick +
                   "! If this is your first time playing, I suggest you start with .rpghelp; otherwise, you can load your previous progress (if any) with .rpgload, or start a new game with .rpgcg.")
    input.conn.msg(
        input.chan, "Once you have a character, the fast track to the dungeon (if you don't want to wander around the town) is .rpgtown dungeon, and then once you're there, .rpgdungeon explore.")
    rpg.destination("town")


@hook.command(autohelp=False)
def rpgload(inp, input=None):
    input.nick = str(input.nick)
    global rpgs
    rpg = rpgs.get(input.nick, None)
    if not rpg:
        return
    if not rpg.validate_player(input):
        return
    d = shelve.open(os.path.expanduser('persist/rpgsaves.db'))
    if input.nick not in d:
        input.conn.msg(input.chan,
                       "You don't currently have a character saved...")
        return
    rpg = d[input.nick]
    d.close()
    input.conn.msg(input.chan,
                   "Game successfully loaded. You're in the town square.")
    rpgs[input.nick] = rpg
    rpg.character.tellchar(input)
    rpg.destination("town")


@hook.command(autohelp=False)
def rpgsheet(inp, input=None):
    input.nick = str(input.nick)
    rpg = rpgs.get(input.nick, None)
    if not rpg:
        return
    if not rpg.validate_player(input):
        return
    if rpg.character.nick != input.nick:
        input.conn.msg(input.chan, "Sorry, " + input.nick +
                       ", you don't have a character sheet for me to show you. Try making one with .rpgcg...")
        return
    if rpg.chardeath == 1:
        input.conn.msg(input.chan, "Sorry, " + input.nick +
                       ", your character is dead, so I tore up the sheet. If you load again, I'll try and find some scotch tape.")
        return
    rpg.character.tellchar(input)
    return


@hook.command(autohelp=False)
def rpgbuy(inp, input=None):
    input.nick = str(input.nick)
    rpg = rpgs.get(input.nick, None)
    if not rpg:
        return
    if not rpg.validate_player(input):
        return
    if rpg.chardeath == 1:
        input.conn.msg(input.chan, "Sorry, " + input.nick +
                       ", you can't buy stuff if you're dead.")
        return
    if rpg.whereareyou != "shop":
        input.conn.msg(input.chan, "You're not shopping right now...")
        return
    opt = inp
    if not opt:
        input.conn.msg(input.chan, "So... what did you want to buy, then?")
        return
    try:
        opt = int(opt.split()[0]) - 1
    except:
        input.conn.msg(input.chan,
                       "The shopkeep has no idea what you're trying to buy.")
        return
    if opt > len(rpg.store) or opt < 0:
        input.conn.msg(
            input.chan, "The shopkeep gives you a strange look. 'How many fingers am I holding up?'")
        return
    buy = rpg.store[opt]
    price = item_worth(buy)
    if price > rpg.character.loot['gp']:
        input.conn.msg(
            input.chan, "Sorry, you don't have enough moola to purchase that item.")
        return
    else:
        input.conn.msg(input.chan, "You snag that swag.")
        rpg.character.buy_loot(buy, price)
        del rpg.store[opt]
        msg1 = "Shop inventory: "
        msg1 += " ".join(rpg.display_itemlist(rpg.store)) + "."
        input.conn.msg(input.chan, msg1)
        msg2 = "Your loot bag: " + str(rpg.character.loot['gp']) + " gp, and "
        msg2 += " ".join(rpg.display_itemlist(rpg.character.loot['items'], True)) + \
            "."
        input.conn.msg(input.chan, msg2)
        return


@hook.command(autohelp=False)
def rpgsell(inp, input=None):
    input.nick = str(input.nick)
    rpg = rpgs.get(input.nick, None)
    if not rpg:
        return
    if not rpg.validate_player(input):
        return
    if rpg.chardeath == 1:
        input.conn.msg(input.chan, "Sorry, " + input.nick +
                       ", you can't sell stuff if you're dead.")
        return
    if rpg.whereareyou != "shop":
        input.conn.msg(input.chan, "You're not shopping right now...")
        return
    opt = inp
    if not opt:
        input.conn.msg(input.chan, "So... what did you want to sell, then?")
        return
    oo = opt.split()
    try:
        opt = int(oo[0]) - 1
    except:
        input.conn.msg(input.chan,
                       "The shopkeep has no idea what you're trying to sell.")
        return
    lootbag = collapse_list(rpg.character.loot['items'], True)
    if opt > len(lootbag) or opt < 0:
        input.conn.msg(
            input.chan, "The shopkeep gives you a strange look. 'How many fingers am I holding up?'")
        return
    sell = lootbag[opt]
    price = max([item_worth(sell) / 2, 1])
    num = 1
    maxnum = [x.lower()
              for x in rpg.character.loot['items']].count(sell.lower())
    if len(oo) > 1:
        print oo[1]
        if oo[1].lower() == 'all':
            num = maxnum
        else:
            try:
                num = int(oo[1])
            except:
                input.conn.msg(
                    input.chan, "I can't tell how many of that you want to sell, so we're going to go with just one.")
                num = 1
    if num > maxnum:
        input.conn.msg(
            input.chan, "You're trying to sell too many of those, so I'm going to sell all of them.")
        num = maxnum
    elif num < 0:
        input.conn.msg(
            input.chan, "You can't sell a negative amount, that's called 'buying'. How's about we just sell one.")
        num = 1
    elif num == 0:
        input.conn.msg(
            input.chan, "Well... OK, I guess.  You sell zero items, and receive 0 gp.")
        return
    if rpg.character.sell_loot(sell, num):
        input.conn.msg(
            input.chan, "You exchange goods for gps, and the shopkeep stashes the loot in his back room.")
    msg1 = "Shop inventory: "
    msg1 += " ".join(rpg.display_itemlist(rpg.store)) + "."
    input.conn.msg(input.chan, msg1)
    msg2 = "Your loot bag: " + str(rpg.character.loot['gp']) + " gp, and: "
    fin = rpg.display_itemlist(rpg.character.loot['items'], True)
    if fin:
        msg2 += " ".join(fin) + "."
    else:
        msg2 += "Nothing!"
    input.conn.msg(input.chan, msg2)
    return


@hook.command(autohelp=False)
def rpgturn(inp, input=None):
    input.nick = str(input.nick)
    rpg = rpgs.get(input.nick, None)
    if not rpg:
        return
    if not rpg.validate_player(input):
        return
    if rpg.chardeath == 1:
        input.conn.msg(input.chan, "Sorry, " + input.nick +
                       ", this game doesn't have zombie-mode support yet.")
        return
    opt = inp
    if not opt:
        input.conn.msg(input.chan, "So... what did you want to do, then?")
        return
    opt = opt.split()
    o = opt[0].lower()
    if o == 'equip':
        if len(opt) < 2:
            input.conn.msg(input.chan, "You're not going to equip anything?")
            return
        o1 = [x.lower().capitalize() for x in opt[1:]]
        ox = ' '.join(o1)
        if ox == rpg.character.loot['quest']:
            input.conn.msg(
                input.chan, "You can't equip the quest item... it's too AWESOME for you, nyah nyah")
            return
        if ox not in rpg.character.loot['items']:
            input.conn.msg(
                input.chan, "You don't have one of those, or it's already equipped.")
            return
        typ = item_type(ox)
        if typ == 'ring':
            neweq = {'ring': ox}
        elif 'weapon' in typ:
            neweq = {'weapon': ox}
        elif 'armor' in typ:
            neweq = {'armor': ox}
        else:
            input.conn.msg(input.chan,
                           "Sorry, there's been an equipment malfunction.")
            return
        rpg.character.equip(neweq)
        input.conn.msg(input.chan, ox + " equipped!")
        if rpg.whereareyou == "combat":
            rpg.combat.advance_turn(input, rpg, rpg.character)
        return
    if rpg.whereareyou != "combat":
        if rpg.whereareyou == "puzzle":
            input.conn.msg(input.chan, "Whatever you were going to do, you steal a look at the " +
                           rpg.puzzle.thing + ", and decide against it.")
        elif o == 'flee':
            input.conn.msg(
                input.chan, "You run away from your own shadow, but it KEEPS CHASING YOU AAAAAAAAAAAAAAAAAAARGH")
        elif rpg.whereareyou == "shop":
            input.conn.msg(
                input.chan, "The shopkeep nimbly avoids your attack, and waggles a finger at you. 'Ah-ah-ah, that's no way to earn a discount!'")
        else:
            input.conn.msg(input.chan,
                           "You swing at the air, which dies a little.")
        return
    if o == 'attack':
        rpg.attack_enemy(input, rpg.character, rpg.combat.enemy)
        return
    if o == 'flee':
        if rpg.runaway(input, rpg.character):
            rpg.destination("dungeon")
            rpg.combat = None
        else:
            rpg.combat.advance_turn(input, rpg, rpg.character)
        return
    if o == 'skill':
        if len(opt) < 2:
            if len(rpg.character.skill) == 1:
                input.conn.msg(input.chan, "You use the skill: " +
                               rpg.character.skill[0] + "!")
                res = rpg.use_skill(
                    input, rpg.character.skill[0], rpg.character, rpg.combat.enemy)
                if res == 0:
                    input.conn.msg(input.chan, "You don't have that skill.")
                    return
                if res == 1:
                    input.conn.msg(
                        input.chan, "You don't have enough skill points remaining to use that skill.")
                    return
                else:
                    return
            else:
                input.conn.msg(input.chan, "You need to specify a skill.")
                return
        o1 = opt[1]
        if o1.lower() in [i.lower() for i in rpg.character.skill]:
            input.conn.msg(input.chan, "You use the skill: " +
                           opt[1].lower().capitalize() + "!")
            res = rpg.use_skill(
                input, opt[1].lower().capitalize(), rpg.character, rpg.combat.enemy)
            return
        else:
            input.conn.msg(input.chan,
                           "You need to specify a skill that you actually have.")
            return
        if res == 0:
            input.conn.msg(input.chan, "You don't have that skill.")
            return
        if res == 1:
            input.conn.msg(
                input.chan, "You don't have enough skill points remaining to use that skill.")
            return
        else:
            return
    else:
        input.conn.msg(input.chan, "You do what with the what now?")
        return


@hook.command(autohelp=False)
def rpgtown(inp, input=None):
    input.nick = str(input.nick)
    rpg = rpgs.get(input.nick, None)
    if not rpg:
        return
    if not rpg.validate_player(input):
        return
    if rpg.chardeath == 1:
        input.conn.msg(input.chan, "Sorry, " + input.nick +
                       ", your character has already been buried in the town cemetary, too deep to dig out.")
        return
    if rpg.whereareyou == "shop":
        input.conn.msg(input.chan,
                       "You leave the shop and head back into the town square.")
        rpg.destination("town")
        return
    if rpg.whereareyou == "shrine":
        input.conn.msg(
            input.chan, "You leave the shrine and head back into the town square.")
        rpg.destination("town")
        return
    if rpg.whereareyou == "puzzle":
        input.conn.msg(
            input.chan, "Wow, is the puzzle really so hard that you want to go back to bed? You have to step it up, man, if you wanna be a True hero...")
        return
    if rpg.whereareyou != "town":
        input.conn.msg(
            input.chan, "You're in the dungeon, dimwit. You'd think the dank air and growl of monsters would have clued you in...")
        return
    opt = inp
    if not opt:
        rpg.telltown(input)
        return
    opt = opt.split()
    if opt[0].lower() == 'dungeon':
        rpg.save()
        if len(opt) < 2:
            input.conn.msg(input.chan, "You head into the dungeon.")
            rpg.dungeonlevel = 1
            rpg.destination("start")
            return
        else:
            try:
                lvl = int(opt[1])
            except:
                lvl = 1
            if lvl > rpg.maxdgnlevel:
                input.conn.msg(
                    input.chan, "You haven't found the stairs to that level yet.")
                return
            rpg.dungeonlevel = lvl
            input.conn.msg(input.chan, "You head to level " +
                           str(lvl) + " of the dungeon.")
            rpg.destination("start")
            return
    elif opt[0].lower() == 'shrine':
        rpg.visit_shrine(input)
        return
    elif opt[0].lower() == 'shop':
        rpg.visit_shop(input)
        return
    elif opt[0].lower() == 'quest':
        rpg.questhall(input)
        return
    elif opt[0].lower() == 'rest':
        input.conn.msg(
            input.chan, "You hit the sack. Once you've annoyed all the bedbugs with your ineffectual fists, you lay down and sleep.")
        rpg.character.sleep()
        rpg.save()
        return
    else:
        input.conn.msg(input.chan,
                       "Sorry, I didn't recognize that command. Try again?")
        return


@hook.command(autohelp=False)
def rpgdungeon(inp, input=None):
    input.nick = str(input.nick)
    rpg = rpgs.get(input.nick, None)
    if not rpg:
        return
    if not rpg.validate_player(input):
        return
    if rpg.chardeath == 1:
        input.conn.msg(input.chan, "Sorry, " + input.nick +
                       ", your character is dead, so you can't explore the dungeon.")
        return
    if rpg.whereareyou == "town":
        tvn = namegen.taverngen()[0]
        input.conn.msg(
            input.chan, "You're not in the dungeon, you're in town. Have you been drinking at the " + tvn + "again?")
        return
    if rpg.whereareyou == "shop":
        input.conn.msg(
            input.chan, "You're in the shop. There's a secret door into the dungeon behind the canned goods, but the shopkeep certainly won't let you in...")
        return
    if rpg.whereareyou == "combat":
        input.conn.msg(
            input.chan, "You... are already fighting something? I mean, you can wander around while being bludgeoned to death with your own stupidity, but I don't recommend it.")
        return
    if rpg.whereareyou == "puzzle":
        input.conn.msg(input.chan, "If I were you, I wouldn't leave a " +
                       rpg.puzzle.thing + " hanging like that...")
    opt = inp
    if not opt:
        input.conn.msg(input.chan, "So... what did you want to do, then?")
        return
    opt = opt.split()[0].lower()
    if opt == 'explore':
        if rpg.whereareyou == "stairs":
            rpg.godownstairs(input)
            return
        else:
            input.conn.msg(input.chan, "You head deeper into the dungeon...")
            rpg.destination("dungeon")
            rpg.explore(input)
            return
    elif opt == 'backtrack':
        if rpg.whereareyou == "start":
            input.conn.msg(
                input.chan, "You're already at the beginning of the level, Captain Redundant.")
            return
        if rpg.whereareyou == "stairs":
            input.conn.msg(input.chan, "You decide to hang around on level " +
                           str(rpg.dungeonlevel) + " a little while longer.")
            rpg.destination("dungeon")
            return
        if rpg.check_backtrack():
            input.conn.msg(
                input.chan, "You successfully find your way back to the beginning of the level.")
            rpg.destination("start")
            return
        else:
            input.conn.msg(
                input.chan, "On your way back, you get lost! You find yourself in another room of the dungeon...")
            rpg.explore(input)
            return
    elif opt == 'return':
        if rpg.whereareyou != "start":
            input.conn.msg(
                input.chan, "You can't go back to town unless you're at the beginning of the level...")
            return
        rpg.destination("town")
        input.conn.msg(input.chan, "You head back to town.")
        return
    else:
        input.conn.msg(input.chan,
                       "Sorry, I didn't recognize that command. Try again?")
        return


@hook.command(autohelp=False)
def rpgpuzzle(inp, input=None):
    input.nick = str(input.nick)
    rpg = rpgs.get(input.nick, None)
    if not rpg:
        return
    if not rpg.validate_player(input):
        return
    if rpg.chardeath == 1:
        input.conn.msg(input.chan, "Sorry, " + input.nick +
                       ", your character is dead, so you can't do puzzle-y things... at least, not in this game, not until you have an alive character.")
        return
    if rpg.whereareyou != "puzzle":
        input.conn.msg(input.chan,
                       "You're not being tested right now... lucky for you!")
        return
    opt = inp
    if not opt and rpg.puzzle.choice != "knowledge":
        input.conn.msg(input.chan, "The " + rpg.puzzle.thing +
                       " is not amused by your hesitation.")
        return
    if not rpg.puzzle.choice:
        if isinstance(opt, list):
            opt = opt[0]
        if opt.lower() in ["gold", "riches", "knowledge", "skip"]:
            rpg.puzzle.puzzleinit(input, rpg, opt)
            return
        else:
            input.conn.msg(input.chan, "The " + rpg.puzzle.thing +
                           " is not amused. 'Make your choice, mortal. My patience grows short.'")
            return
    else:
        if rpg.puzzle.choice == "gold":
            rpg.puzzle.check_numguess(input, rpg, opt)
            return
        elif rpg.puzzle.choice == "riches":
            rpg.puzzle.check_riddleguess(input, rpg, opt)
            return
        elif rpg.puzzle.choice == "knowledge":
            rpg.puzzle.trialofbeing(input, rpg)
        else:
            input.conn.msg(input.chan, "There's been a puzzle malfunction...")


@hook.command(autohelp=False)
def rpgshrine(inp, input=None):
    input.nick = str(input.nick)
    rpg = rpgs.get(input.nick, None)
    if not rpg:
        return
    if not rpg.validate_player(input):
        return
    if rpg.chardeath == 1:
        input.conn.msg(input.chan, "Sorry, " + input.nick +
                       ", your character is dead, and the Unknowable Gods are busy consuming its soul, so they can't pay attention to offerings.")
        return
    if rpg.whereareyou != "shrine":
        input.conn.msg(input.chan, "You're not in the Shrine right now...")
        return
    opt = inp
    if not opt:
        input.conn.msg(input.chan, "Yes. Shrine. OK?")
        return
    opt = opt.split()
    amt = 0 if len(opt) == 1 else opt[1]
    try:
        amt = int(amt)
    except:
        input.conn.msg(input.chan,
                       "Hey! No funny business with the offering, bucko.")
        return
    choice = opt[0]
    if choice != '1' and choice != '2':
        input.conn.msg(
            input.chan, "You toss an offering into some imaginary bowl, and it clatters onto the floor. You scoop it up again before anyone notices.")
        return
    rpg.offering(input, choice, amt)
    return


@hook.command('rpgcg', autohelp=False)
def rpgcg(inp, input=None):
    input.nick = str(input.nick)
    rpg = rpgs.get(input.nick, None)
    if not rpg:
        return
    if not rpg.validate_player(input):
        return
    if rpg.character.name and not rpg.chardeath:
        input.conn.msg(
            input.chan, "You have an active character already... if you really want to make a new one, please quit and restart the game.")
        return
    opts = inp
    race = ''
    cls = ''
    fts = []
    nfeat = 1
    if not opts:
        pass
    else:
        opts = opts.split()
        nfeat = 1
        for o in opts:
            if o.lower() in draces.keys():
                race = o
                if race == 'human':
                    nfeat = 2
            if o.lower() in dclasses.keys():
                cls = o
            for j in dfeats.keys():
                if o.lower() == j.lower():
                    if len(fts) + 1 > nfeat:
                        input.conn.msg(
                            input.chan, "You've chosen too many feats; I'll take them in the order you gave them.")
                    else:
                        fts.append(j)
    if not race:
        race = random.choice([random.choice(draces.keys())
                             for i in range(0, 6)])
    if not cls:
        cls = random.choice([random.choice(dclasses.keys())
                            for i in range(0, 6)])
    if not fts:
        nfeat = 1
        if race == 'human':
            nfeat = 2
        fts = []
        for i in range(0, nfeat):
            fts.append(random.choice([random.choice(dfeats.keys())
                       for j in range(0, 6)]))
    if nfeat == 2 and len(fts) == 1:
        fts.append(random.choice([random.choice(dfeats.keys())
                   for j in range(0, 6)]))
    rpg.character.chargen(input.nick, race, cls, fts)
    rpg.new_char()
    rpg.destination("town")
    rpg.save()
    msg = "In the town of North Granby, the town militia has recently discovered that the plague of monsters harrassing the townspeople originates from a nearby dungeon crammed with nasties."
    msg += " As the resident adventurer, the Mayor of North Granby (a retired adventurer by the name of Sir Percival) has recruited you to clear out the dungeon."
    input.conn.msg(input.chan, msg)
    rpg.character.tellchar(input)
    rpg.telltown(input, True)


@hook.command(autohelp=False)
def rpglvlup(inp, input=None):
    input.nick = str(input.nick)
    rpg = rpgs.get(input.nick, None)
    if not rpg:
        return
    if not rpg.validate_player(input):
        return
    if rpg.chardeath:
        input.conn.msg(
            input.chan, "Sorry, you can't level up because your character is dead.")
        return
    lim = rpg.character.level * 10
    if rpg.character.exp < lim:
        input.conn.msg(input.chan, "Sorry, it's not time for you to level up yet. You need " +
                       str(lim - rpg.character.exp) + " more experience.")
        return
    opt = inp
    if not opt:
        rpg.character.levelup(
            random.choice([random.choice(dfeats.keys()) for j in range(0, 6)]))
        return
    opt = opt.split()
    if len(opt) > 1:
        input.conn.msg(
            input.chan, "You picked too many feats! I'll use the first one I recognize.")
    for i in opt:
        for j in dfeats.keys():
            if i.lower() == j.lower():
                rpg.character.levelup(j)
                input.conn.msg(input.chan, "You have leveled up! You gained the " + j + " feat, and now have " +
                               str(rpg.character.hp) + " hit points and " + str(rpg.character.sp) + " skill points.")
                return
    input.conn.msg(
        input.chan, "I didn't recognize your feat choice, sorry. You can try again; use .rpghelp feats to see the list of available feats.")


@hook.command(autohelp=False)
def rpgwhere(input):
    input.nick = str(input.nick)
    rpg = rpgs.get(input.nick, None)
    if not rpg:
        return
    if not rpg.validate_player(input):
        return
    wh = rpg.whereareyou
    if wh == 'dungeon':
        input.conn.msg(input.chan, "You're in the dungeon, on level " +
                       str(rpg.dungeonlevel) + ".")
    elif wh == 'town':
        input.conn.msg(input.chan, "You're in the town square.")
    elif wh == 'shop':
        input.conn.msg(input.chan, "You're in the General Store.")
    elif wh == 'combat':
        trn = " your " if rpg.combat.turnorder[
            rpg.combat.turn % 2] == "player" else " the monster's "
        input.conn.msg(input.chan,
                       "You're in the middle of a fight! It's" + trn + "turn.")
    elif wh == 'start':
        input.conn.msg(input.chan, "You're in the dungeon, at the beginning of level " +
                       str(rpg.dungeonlevel) + ".")
    elif wh == 'stairs':
        input.conn.msg(
            input.chan, "You're in the dungeon, standing atop a flight of stairs.")
    elif wh == 'puzzle':
        input.conn.msg(input.chan, "You're testing your mettle against a " +
                       rpg.puzzle.thing + ", of course.")
    elif wh == 'shrine':
        input.conn.msg(input.chan, "You're bumbling around in the Shrine.")
    else:
        input.conn.msg(input.chan, "Hm, I don't know /where/ you are.")


@hook.command(autohelp=False)
def rpgquit(inp, input=None):
    input.nick = str(input.nick)
    rpg = rpgs.get(input.nick, None)
    if not rpg:
        return
    if not rpg.validate_player(input):
        return
    input.conn.msg(input.chan, "Well... see you later, I guess... *sob*")
    input.conn.send('PART ' + rpg.game_channel)
    del rpgs[input.nick]


@hook.command('rpga', autohelp=False)
def rpg_active(inp, input=None):
    # if input.nick != 'bears':
    #   returni
    global rpgs
    if not rpgs:
        input.conn.msg(input.chan, "No active games right now.")
    else:
        chans = []
        for i in rpgs.keys():
            chans.append(rpgs[i].game_channel)
        input.conn.msg(input.chan, ', '.join(chans))


@hook.command(autohelp=False)
def rpghelp(inp, input=None):
    input.nick = str(input.nick)
    rpg = rpgs.get(input.nick, None)
    if not rpg:
        return
    if not rpg.validate_player(input):
        return
    # topics:
    topic = inp
    if not topic:
        input.conn.msg(
            input.chan, "Welcome to Percival's Quest! Here's a list of help topics: Commands [can also ask for help on each individual command], Backtrack, Classes, Dungeon, Equip, Explore, Feats, Game, Puzzles, Quest, Races, Rest, Shop, Shrine, Skills, Stats, Treasure. You can also get a more complete version of this help at http://eikorpg.wikia.com/wiki/EikoRPG_Wiki")
        return
    topic = topic.lower()
    if topic == 'commands':
        input.conn.msg(
            input.chan, "Here is the list of possible commands (each should be preceded with a '.' when using): rpg, rpghelp, rpgbuy, rpgcg, rpgdungeon, rpginit, rpglvlup, rpgload, rpgpuzzle, rpgquit, rpgsell, rpgsheet, rpgshrine, rpgtown, rpgturn, rpgwhere")
    elif topic == 'rpghelp' or topic == 'topics':
        input.conn.msg(
            input.chan, "Welcome to Percival's Quest! Here's a list of help topics: Commands [can also ask for help on each individual command], Backtrack, Classes, Dungeon, Equip, Explore, Feats, Game, Puzzles, Quest, Races, Rest, Shop, Shrine, Skills, Stats, Treasure. You can also get a more complete version of this help at http://eikorpg.wikia.com/wiki/EikoRPG_Wiki")
    elif topic == 'rpgcg':
        input.conn.msg(
            input.chan, "Once you've begun a new game, this is how you generate your character. Syntax: .rpgcg [race] [class] [feats] -- note that if you don't provide them, any and all of those will be randomly generated.")
    elif topic == 'rpg':
        input.conn.msg(input.chan,
                       "This is how you start the game in the main channel.")
    elif topic == 'rpgdungeon':
        input.conn.msg(
            input.chan, "This is how you explore the dungeon. Syntax: .rpgdungeon option -- options are Explore, Backtrack, or Return (to town). You can only return to town when you are at the beginning of a level; otherwise, you have to backtrack, which may or may not work.")
    elif topic == 'rpginit':
        input.conn.msg(
            input.chan, "This command initializes the game when you enter the channel. Syntax: .rpginit")
    elif topic == 'rpgload':
        input.conn.msg(
            input.chan, "When you initialize the game, use this command to load your progress, or .rpgcg to start a new game. Syntax: .rpgload")
    elif topic == 'rpgtown':
        input.conn.msg(
            input.chan, "Back in town, this lets you select your next move. Syntax: .rpgtown option -- options are Dungeon [level] (note that you can only visit dungeon levels you've been to before), Questhall, Rest, Shrine, or Shop.")
    elif topic == 'rpgturn':
        input.conn.msg(
            input.chan, "If you're in combat, use this command to act. Syntax: .rpgturn action -- actions are Attack, Equip, Flee, Skill [skill].")
    elif topic == 'backtrack':
        input.conn.msg(
            input.chan, "An option for .rpgdungeon to go back to the beginning of the level (so you can return to town). Your chance of backtracking successfully depends on your Will score.")
    elif topic == 'classes':
        input.conn.msg(input.chan, "The available classes are: " +
                       ", ".join(sorted(dclasses.keys())))
    elif topic == 'dungeon':
        input.conn.msg(
            input.chan, "An option for .rpgtown to enter the dungeon. You may specify a level number for a level you've already visited, and you'll go directly to that level.")
    elif topic == 'explore':
        input.conn.msg(
            input.chan, "An option for .rpgdungeon to explore the next room in the current level. When exploring a room, you'll find one of the following: a Monster, a Chest, an Empty Room (with a Sandwich), a Puzzle Encounter, or Stairs. In the future, bears may add Traps to the list.")
    elif topic == 'feats':
        input.conn.msg(input.chan, "The available feats are: " +
                       ", ".join(sorted(dfeats.keys())))
    elif topic == 'game':
        input.conn.msg(
            input.chan, "This is Percival's Quest, an IRC RPG originally written by sirpercival and updated by bears.")
    elif topic == 'quest':
        input.conn.msg(
            input.chan, "An option for .rpgtown to visit the Questhall. At the Questhall, you will be given a quest to retrieve a certain item from a certain unique monster. There's one quest per dungeon level, and you have to complete them in order (though you can explore other dungeon levels, you won't encounter the quest monster off-level). When you complete a quest, you will be given... rewards.")
    elif topic == 'races':
        input.conn.msg(input.chan, "The available races are: " +
                       ", ".join(sorted(draces.keys())))
    elif topic == 'rest':
        input.conn.msg(
            input.chan, "An option for .rpgtown to regain your HP and SP, and autosave. You can only rest while in town, though if you find a sandwich in the dungeon, you'll regain a small amount.")
    elif topic == 'shop':
        input.conn.msg(
            input.chan, "An option for .rpgtown to visit the shop so you can sell loot and buy equipment.")
    elif topic == 'equip':
        input.conn.msg(
            input.chan, "An option for .rpgturn to equip an item, unequipping whatever you have in the same slot (if anything). You can also use this out of combat.")
    elif topic == 'skills':
        input.conn.msg(input.chan, "The available skills are: " +
                       ", ".join(sorted(dskill.values())))
    elif topic == 'stats':
        input.conn.msg(
            input.chan, "Percival's Quest has 6 attributes ('stats'): Attack, which governs your physical attack prowess; Defense, which governs your defense against physical attacks; Reflex, which determines your initiative and your defense against some skills;")
        input.conn.msg(
            input.chan, "Fortitude, which determines your hit points and your defense against some skills; Mind, which affects your backtrack chance and your defense against some skills; and Skill, which determines your skill points and the effectiveness of your skills.")
    elif topic == 'treasure':
        input.conn.msg(
            input.chan, "When you defeat a monster or find a chest, you may find some loot, in the form of gold (GP), armors, weapons, or rings. bears may add potions sometime in the future.")
    elif topic == 'rpgquit':
        input.conn.msg(
            input.chan, "The command to quit the game. Please do this when you're done playing!")
    elif topic == 'rpglvlup':
        input.conn.msg(
            input.chan, "Use this command to pick your feat when you gain a level. Syntax: .rpglvlup [feat] -- .rpghelp feats will give you the list of available feats. If you don't supply a feat, one will be chosen for you at random.")
    elif topic == 'rpgbuy':
        input.conn.msg(
            input.chan, "Buy stuff from the shop with this command. Syntax: .rpgbuy itemnumber")
    elif topic == 'rpgsell':
        input.conn.msg(
            input.chan, "Sell stuff back to the shop with this command. Syntax: .rpgsell lootnumber")
    elif topic == 'rpgwhere':
        input.conn.msg(input.chan, "Tells you where you are.")
    elif topic == 'rpgsheet':
        input.conn.msg(input.chan,
                       "A command to display your character sheet.")
    elif topic == 'rpgshrine':
        input.conn.msg(
            input.chan, "The command to make an offering at the Shrine of the Unknowable Gods. In the Shrine, you can make offerings to Enlightenment (choice '1') or Materialism (choice '2'). Syntax: .rpgshrine choice offering_amount")
    elif topic == 'shrine':
        input.conn.msg(input.chan,
                       "An option for .rpgtown to visit the Shrine.")
    elif topic == 'puzzles':
        input.conn.msg(
            input.chan, "In the Dungeon, you might find a puzzle encounter. You can either try to solve a riddle, play a number guessing game, or undergo the Trial of Being.")
    elif topic == 'rpgpuzzle':
        input.conn.msg(
            input.chan, "This is how you interact with the puzzle encounter. Syntax: .rpgpuzzle choice/guess -- first make a choice of the type of reward (gold, riches, knowledge, or skip to leave the encounter), then use .rpgpuzzle to enter your guesses.")
    else:
        input.conn.msg(
            input.chan, "I'm sorry, I don't recognize that topic. Try .rpghelp topics for a list of topics I can help you with.")
