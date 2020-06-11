import re
from util import hook


def db_init(db):
    db.execute("create table if not exists karma(chan text, nick text, op text,"
        "item text, score integer, primary key(chan, nick, op, item))")
    db.commit()


def is_global(inp):
    _inp = ' '.join([t for t in inp.split(' ') if t.lower() != '-g'])
    if inp == _inp:
        return inp, False
    else:
        return _inp, True


@hook.regex(r'(\(.*\)|\S+)(\+\+|--)')
def karma_edit(inp, chan='', nick='', db=None):
    db_init(db)

    inp, op = inp.groups()
    inp = inp.strip('() ').lower()

    if inp == nick.lower():
        return #"Please do not karma yourself."

    row = db.execute("select ifnull(sum(case when score > 0 then score else 0 end), 0) positive, ifnull(sum(case when score < 0 then score else 0 end), 0) negative from karma where chan=lower(?) and nick=lower(?) and item=lower(?)", (chan, nick, inp)).fetchone()
    karma = dict(zip(['pos', 'neg'], row))

    if op == "++":
        if karma['pos'] > 0:
            db.execute("update karma set score=? where chan=lower(?) and nick=lower(?) and op='++' and item=lower(?)", (karma['pos'] + 1, chan, nick, inp))
        else:
            db.execute("insert into karma (chan, nick, op, item, score) values(lower(?), lower(?), '++', lower(?), 1)", (chan, nick, inp))
    elif op == "--":
        if karma['neg'] < 0:
            db.execute("update karma set score=? where chan=lower(?) and nick=lower(?) and op='--' and item=lower(?)", (karma['neg'] - 1, chan, nick, inp))
        else:
            db.execute("insert into karma (chan, nick, op, item, score) values(lower(?), lower(?), '--', lower(?), -1)", (chan, nick, inp))

    db.commit()


@hook.regex(r'^karma (.+)')
@hook.command
def karma(inp, chan='', say=None, db=None, input=None):
    """karma <word> - Returns karma of <word>; <word>(++|--) increments or decrements karma of <word>."""
    try:
        inp = inp.group(1)
    except:
        pass

    db_init(db)

    inp = inp.strip('() ').lower()
    inp, _global = is_global(inp)

    if not inp:
        return "Check your input and try again."

    if _global:
        karma = db.execute("select sum(score), sum(case when score > 0 then score else 0 end) positive, sum(case when score < 0 then score else 0 end) negative from karma where item=lower(?)", (inp, )).fetchone()
        voters = db.execute("select nick, ifnull(sum(score), 0), ifnull(sum(case when score > 0 then score else 0 end), 0) positive, ifnull(sum(case when score < 0 then score else 0 end), 0) negative from karma where item=lower(?) group by nick", (inp, )).fetchall()
    else:
        karma = db.execute("select ifnull(sum(score), 0), ifnull(sum(case when score > 0 then score else 0 end), 0) positive, ifnull(sum(case when score < 0 then score else 0 end), 0) negative from karma where chan=lower(?) and item=lower(?)", (chan, inp)).fetchone()
        voters = db.execute("select nick, ifnull(sum(score), 0), ifnull(sum(case when score > 0 then score else 0 end), 0) positive, ifnull(sum(case when score < 0 then score else 0 end), 0) negative from karma where chan=lower(?) and item=lower(?) group by nick", (chan, inp)).fetchall()

    karma = dict(zip(['net', 'pos', 'neg'], karma))
    voters = [dict(zip(['nick', 'net', 'pos', 'neg'], row)) for row in voters]

    upvoters = sorted(filter(lambda x: x['pos'] > 0, voters), key=lambda x: x['pos'], reverse=True)[0:5]
    upvoters = ', '.join(['{nick} {net:+,d} ({pos:+,d}/{neg:+,d})'.format(**voter) for voter in upvoters])
    downvoters = sorted(filter(lambda x: x['neg'] < 0, voters), key=lambda x: x['neg'])[0:5]
    downvoters = ', '.join(['{nick} {net:+,d} ({pos:+,d}/{neg:+,d})'.format(**voter) for voter in downvoters])


    if karma['net'] == karma['pos'] == karma['neg'] == 0:
        say('"{}" has neutral karma.'.format(inp))
    else:
        if _global:
            say("Karma for '{}': Net karma: {:+,d} ({:+,d}/{:+,d}; {:.1%} like it). Top upvoters: {}. Top downvoters: {}.".format(inp,
                karma['net'], karma['pos'], karma['neg'], float(karma['pos']) / float(karma['pos'] + abs(karma['neg'])),
                upvoters or "None", downvoters or "None"))
        else:
            say("Karma for '{}' in {}: Net karma: {:+,d} ({:+,d}/{:+,d}; {:.1%} like it). Top upvoters: {}. Top downvoters: {}.".format(inp,
                chan, karma['net'], karma['pos'], karma['neg'], float(karma['pos']) / float(karma['pos'] + abs(karma['neg'])),
                upvoters or "None", downvoters or "None"))

