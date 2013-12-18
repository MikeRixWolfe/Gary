from util import hook, web

@hook.command(adminonly=True)
def plpaste(inp, bot=None):
    ".plpaste <plugin> - Hastebin's a plugin's code and returns the link"
    if inp in bot.commands:
        with open(bot.commands[inp][0].func_code.co_filename.strip()) as f:
            return web.haste(f.read(), ext='py')
    else:
        try:
            plugin = open('plugins/%s.py' % inp)
            return  web.haste(plugin.read(), ext='py')
        except:
            pass
                 
        return "Could not find specified plugin."
