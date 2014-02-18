from util import hook, web


@hook.command(adminonly=True)
def plpaste(inp, say='', bot=None):
    ".plpaste <plugin> - Hastebin's a plugin's code and returns the link"
    if inp in bot.commands:
        with open(bot.commands[inp][0].func_code.co_filename.strip()) as f:
            say(web.haste(f.read(), 'py'))
    else:
        try:
            if inp[-3:] == '.py':
                inp = inp[:-3]
            plugin = open('plugins/%s.py' % inp)
            say(web.haste(plugin.read(), 'py'))
            return
        except:
            pass

        return "Could not find specified plugin."
