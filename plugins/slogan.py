from util import hook, text
import random


with open("plugins/data/slogans.txt") as f:
    slogans = [line.strip() for line in f.readlines()]


@hook.command
def slogan(inp, say=''):
    """.slogan <word> - Makes a slogan for <word>."""
    out = random.choice(slogans)
    if inp.lower() and out.startswith("<text>"):
        inp = text.capitalize_first(inp)
    say(out.replace('<text>', inp))

