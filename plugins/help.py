import re
from util import hook, text


def get_help(bot, flag=None):
    funcs = {}
    disabled = bot.config.get('disabled', [])
    for command, (func, args) in bot.commands.iteritems():
        fn = re.match(r'^plugins.(.+\.py)$', func._filename)
        if not any(x in disabled for x in [fn.group(1).lower(), command]):
            if flag == 'admin' \
                    and (args.get('adminonly') or args.get('modonly')):
                if func in funcs:
                    if command == func.func_name:
                        funcs[func] = command
                    else:
                        print func, command
                else:
                    funcs[func] = command
            elif flag == 'mod' and args.get('modonly'):
                if func in funcs:
                    if command == func.func_name:
                        funcs[func] = command
                else:
                    funcs[func] = command
            elif not flag and \
                not (args.get('adminonly') or args.get('modonly')):
                if func in funcs:
                    if command == func.func_name:
                        funcs[func] = command
                else:
                    funcs[func] = command

    return {v:k for k,v in funcs.iteritems()}


@hook.command(autohelp=False, adminonly=True)
def ahelp(inp, say=None, bot=None, input=None):
    """.ahelp [command] - Gives a list of commands or help for a command."""
    commands = get_help(bot, 'admin')

    if not inp:
        out = sorted([k for k,v in commands.iteritems() if v.__doc__])
        for out in text.chunk_str('Available commands: %s' % ' '.join(out)):
            say(out)
        say("Tip: .ahelp <command> - Gets more info on that command; " \
            "arguments in <chevrons> are required, and arguments in " \
            "[brackets] are optional for any command.")
    else:
        if inp in commands:
            say(commands[inp].__doc__ or
                "Command '%s' has no additional documentation." % inp)
        else:
            say("Unknown command.")


@hook.command(autohelp=False, modonly=True)
def mhelp(inp, say=None, bot=None, input=None):
    """.mhelp [command] - Gives a list of commands or help for a command."""
    commands = get_help(bot, 'mod')

    if not inp:
        out = sorted([k for k,v in commands.iteritems() if v.__doc__])
        for out in text.chunk_str('Available commands: %s' % ' '.join(out)):
            say(out)
        say("Tip: .mhelp <command> - Gets more info on that command; " \
            "arguments in <chevrons> are required, and arguments in " \
            "[brackets] are optional for any command.")
    else:
        if inp in commands:
            say(commands[inp].__doc__ or
                "Command '%s' has no additional documentation." % inp)
        else:
            say("Unknown command.")


@hook.command(autohelp=False)
def help(inp, say=None, bot=None, input=None):
    """.help [command] - Gives a list of commands or help for a command."""
    commands = get_help(bot)

    if not inp:
        out = sorted([k for k,v in commands.iteritems() if v.__doc__])
        for out in text.chunk_str('Available commands: %s' % ' '.join(out)):
            say(out)
        say("Tip: .help <command> - Gets more info on that command; " \
            "arguments in <chevrons> are required, and arguments in " \
            "[brackets] are optional for any command.")
    else:
        if inp in commands:
            say(commands[inp].__doc__ or
                "Command '%s' has no additional documentation." % inp)
        else:
            say("Unknown command.")

