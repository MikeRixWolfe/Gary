import re
from util import hook, text


def get_help(bot, adminonly=False):
    funcs = {}
    disabled = bot.config.get('disabled', [])

    for command, (func, args) in bot.commands.iteritems():
        fn = re.match(r'^plugins.(.+\.py)$', func._filename)
        if not any(x in disabled for x in [fn.group(1).lower(), command]):
            if (args.get('adminonly') or False) is adminonly:
                if func in funcs:
                    if command == func.func_name:
                        funcs[func] = command
                else:
                    funcs[func] = command

    return {v:k for k,v in funcs.iteritems()}


@hook.command('ahelp', autohelp=False, adminonly=True)
@hook.command(autohelp=False)
def help(inp, say=None, bot=None, input=None):
    """.help [command] - Gives a list of commands or help for a command."""
    if input.trigger == 'ahelp':  # The adminonly trigger outputs admin commands instead
        commands = get_help(bot, True)
    else:
        commands = get_help(bot)

    if not inp:
        out = sorted([k for k,v in commands.iteritems() if v.__doc__])
        for out in text.chunk_str('Available commands: %s' % ' '.join(out)):
            say(out)
        say('Tip: .help <command> - Gets more info on that command; arguements in <angle brackets> are required and arguements in [square brackets] are optional for any command')
    else:
        if inp in commands:
            say(commands[inp].__doc__ or "Command %s has no additional documentation." % inp)
        else:
            say("Unknown command.")


