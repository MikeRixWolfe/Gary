import re

from util import hook


@hook.command(autohelp=False)
def help(inp, bot=None, say=None):
    ".help [command] - gives a list of commands/help for a command"

    funcs = {}
    disabled = bot.config.get('disabled', [])
    for command, (func, args) in bot.commands.iteritems():
        fn = re.match(r'^plugins.(.+\.py)$', func._filename)
        if fn.group(1).lower() not in disabled:
            if command not in disabled:
                if func.__doc__ is not None:
                    if not args.get('adminonly'):
                        if func in funcs:
                            if len(funcs[func]) < len(command):
                                funcs[func] = command
                        else:
                            funcs[func] = command

    commands = dict((value, key) for key, value in funcs.iteritems())
    commandlist = sorted(commands)
    overflowlist = list()
    if not inp:
        while len('Available commands: ' + ' '.join(commandlist)) >= 460:
            overflowlist.append(commandlist.pop())
        if len(overflowlist) > 0:
            say('Available commands: ' + ' '.join(commandlist))
            say(' '.join(sorted(overflowlist)))
        else:
            say('Available commands: ' + ' '.join(sorted(commands)))
        say('Tip: .help <command> - Gets more info on that command')
    else:
        if inp in commands:
            say(commands[inp].__doc__)


@hook.command(autohelp=False, adminonly=True)
def adminhelp(inp, bot=None, say=None):
    ".adminhelp [command] - gives a list of admin commands/help for a command"

    funcs = {}
    disabled = bot.config.get('disabled', [])
    for command, (func, args) in bot.commands.iteritems():
        fn = re.match(r'^plugins.(.+\.py)$', func._filename)
        if fn.group(1).lower() not in disabled:
            if command not in disabled:
                if func.__doc__ is not None:
                    if args.get('adminonly'):
                        if func in funcs:
                            if len(funcs[func]) < len(command):
                                funcs[func] = command
                        else:
                            funcs[func] = command

    commands = dict((value, key) for key, value in funcs.iteritems())
    commandlist = sorted(commands)
    overflowlist = list()
    if not inp:
        while len('Available commands: ' + ' '.join(commandlist)) >= 460:
            overflowlist.append(commandlist.pop())
        if len(overflowlist) > 0:
            say('Available commands: ' + ' '.join(commandlist))
            say(' '.join(sorted(overflowlist)))
        else:
            say('Available commands: ' + ' '.join(sorted(commands)))
    else:
        if inp in commands:
            say(commands[inp].__doc__)
