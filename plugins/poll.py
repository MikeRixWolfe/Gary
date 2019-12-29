from collections import defaultdict
from json import dumps
from re import findall
from util import hook, web


def tree():  # autovivification
    return defaultdict(tree)

active_polls = tree()


@hook.command(autohelp=True)
def poll(inp, nick=None, chan=None, say=None):
    """poll <description>[: choice1, choice2, ..., choice n] - Begins a poll if you do not already have an active poll; choices default to [yes|no]; end poll and get results with '.poll close'."""
    global active_polls
    active_polls[chan]  # init

    if inp == "close":
        if active_polls.get(chan).get(nick) is None:
            return "You do not have an active poll."
        else:
            active_polls[chan][nick]['results']['total'] = len(active_polls[chan][nick]['votes'].keys())
            for choice in active_polls[chan][nick]['choices']:
                active_polls[chan][nick]['results']['choices'][choice] = len([x for x in active_polls[chan][nick]['votes'] if active_polls[chan][nick]['votes'][x] == choice])
            results = web.haste(dumps(active_polls.get(chan).get(nick), sort_keys=True, indent=2))
            del active_polls[chan][nick]
            say("Results for {}'s poll: {}".format(nick, results))
    elif active_polls.get(chan).get(nick) is not None:
        return "You already have an active poll: '{}'.".format(active_polls[chan][nick]['description'])
    else:
        if ':' in inp:
            desc, choices = inp.split(':')
            c = findall(r'([^,]+)', choices)
            if len(c) == 1:
                c = findall(r'(\S+)', choices)
            choices = list(set(x.strip() for x in c))
        else:
            desc = inp
            choices = ["yes", "no"]

        active_polls[chan][nick]['description'] = desc
        active_polls[chan][nick]['choices'] = choices
        active_polls[chan][nick]['votes']
        say("Poll '{1}' started by {0}; to vote use '.vote {0} <{2}>'.".format(nick, desc, "|".join(choices)))


@hook.command(autohelp=False)
def polls(inp, chan=None, say=None):
    """polls [user] - Gets a list of active polls, or information on a specific poll."""
    global active_polls
    active_polls[chan]  # init

    if inp:
        if active_polls.get(chan).get(inp):
            say("{}'s '{}' poll choices: {}".format(inp, active_polls.get(chan).get(inp).get('description'), ', '.join(active_polls.get(chan).get(inp).get('choices'))))
        else:
            say("No active poll for {}.".format(inp))
    else:
        say("Active polls: {}".format((", ".join(active_polls.get(chan).keys()) if active_polls.get(chan) else "None")))


@hook.command(autohelp=True)
def vote(inp, nick=None, chan=None):
    """vote <poll owner> <choice> - Vote on a poll; responds on error and silently records on success."""
    global active_polls
    active_polls[chan]  # init

    if len(inp.split(' ', 1)) == 2:
        poll, vote = inp.split(' ', 1)
        if active_polls.get(chan).get(poll) is None:
            return "The poll you are trying to vote for no longer exists."
        if vote not in active_polls.get(chan).get(poll).get('choices'):
            return "Invalid vote; valid choices are: {}".format(', '.join(active_polls.get(chan).get(poll).get('choices')))
    else:
        return "Please use form '.vote <poll owner> <choice>'; check active polls with '.polls'."

    active_polls[chan][poll]['votes'][nick] = vote

