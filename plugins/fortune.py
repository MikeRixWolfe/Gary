import random
from util import hook


@hook.command(autohelp=False)
def fortune(inp):
    """.fortune - Returns random fortune."""
    with open("plugins/data/fortunes.txt") as f:
        fortunes = [line.strip() for line in f.readlines()
            if not line.startswith("//")]
    return random.choice(fortunes)
