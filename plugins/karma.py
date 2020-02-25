import re
from util import hook


def db_init(db):
    db.execute("create table if not exists karma(chan text, nick text, op text,"
        "item text, score integer, primary key(chan, nick, op, item))")
    db.commit()


def get_karma(db, item):
    row = db.execute("select sum(score), sum(case when score > 0 then score else 0 end) positive, sum(case when score < 0 then score else 0 end) negative from karma where item=lower(?)",
        (item, )).fetchone()
    return {'net': row[0] or 0, 'pos': row[1] or 0, 'neg': row[2] or 0} if row else {}


def get_karma_chan(db, chan, item):
    row = db.execute("select sum(score), sum(case when score > 0 then score else 0 end) positive, sum(case when score < 0 then score else 0 end) negative from karma where chan=lower(?) and item=lower(?)",
        (chan, item)).fetchone()
    return {'net': row[0] or 0, 'pos': row[1] or 0, 'neg': row[2] or 0} if row else {}


def get_karma_user(db, chan, nick, item):
    row = db.execute("select sum(case when score > 0 then score else 0 end) positive, sum(case when score < 0 then score else 0 end) negative from karma where chan=lower(?) and nick=lower(?) and item=lower(?)",
        (chan, nick, item)).fetchone()
    return {'pos': row[1] or 0, 'neg': row[2] or 0} if row else {}


def get_voters(db, item):
    rows = db.execute("select nick, sum(score), sum(case when score > 0 then score else 0 end) positive, sum(case when score < 0 then score else 0 end) negative from karma where item=lower(?) group by nick",
        (item, )).fetchall()
    return [{'nick': row[0], 'net': row[1], 'pos': row[2], 'neg': row[3]} for row in rows]


def get_voters_chan(db, chan, item):
    rows = db.execute("select nick, sum(score), sum(case when score > 0 then score else 0 end) positive, sum(case when score < 0 then score else 0 end) negative from karma where chan=lower(?) and item=lower(?) group by nick",
        (chan, item)).fetchall()
    return [{'nick': row[0], 'net': row[1], 'pos': row[2], 'neg': row[3]} for row in rows]


@hook.regex(r'(\(.*\)|\S+)(\+\+|--)')
def karma_edit(inp, chan='', nick='', say=None, db=None):
    db_init(db)

    item, op = inp.groups()
    item = item.strip('() ').lower()

    if item == nick.lower():
        return #"Please do not karma yourself."

    karma = get_karma_chan(db, chan, item)

    if op == "++":
        if karma['pos'] > 0:
            db.execute("update karma set score=? where chan=lower(?) and nick=lower(?) and op='++' and item=lower(?)", (karma['pos'] + 1, chan, nick, item))
            db.commit()
        else:
            db.execute("insert into karma (chan, nick, op, item, score) values(lower(?), lower(?), '++', lower(?), 1)", (chan, nick, item))
            db.commit()
    elif op == "--":
        if karma['neg'] < 0:
            db.execute("update karma set score=? where chan=lower(?) and nick=lower(?) and op='++' and item=lower(?)", (karma['neg'] - 1, chan, nick, item))
            db.commit()
        else:
            db.execute("insert into karma (chan, nick, op, item, score) values(lower(?), lower(?), '--', lower(?), -1)", (chan, nick, item))
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

    try:
        inp = [t for t in inp.split(' ') if t]
        inp.remove('-g')
        g = True
        inp = ' '.join(inp)
    except:
        g = False
        inp = ' '.join(inp)

    if not inp:
        return "Check your input and try again."

    if g:
        karma = get_karma(db, inp)
        voters = get_voters(db, inp)
    else:
        karma = get_karma_chan(db, chan, inp)
        voters = get_voters_chan(db, chan, inp)

    upvoters = sorted(filter(lambda x: x['pos'] > 0, voters), key=lambda x: x['pos'], reverse=True)[0:5]
    upvoters = ', '.join(['{nick} {net:+d} ({pos:+d}/{neg:+d})'.format(**voter) for voter in upvoters])
    downvoters = sorted(filter(lambda x: x['neg'] < 0, voters), key=lambda x: x['neg'])[0:5]
    downvoters = ', '.join(['{nick} {net:+d} ({pos:+d}/{neg:+d})'.format(**voter) for voter in downvoters])


    if karma['net'] == karma['pos'] == karma['neg'] == 0:
        say('"{}" has neutral karma.'.format(inp))
    else:
        if g:
            say("Karma for '{}': Net karma: {:+d} ({:+d}/{:+d}; {:.1%} like it). Top upvoters: {}. Top downvoters: {}.".format(inp,
                karma['net'], karma['pos'], karma['neg'], float(karma['pos']) / float(karma['pos'] + abs(karma['neg'])),
                upvoters or "None", downvoters or "None"))
        else:
            say("Karma for '{}' in {}: Net karma: {:+d} ({:+d}/{:+d}; {:.1%} like it). Top upvoters: {}. Top downvoters: {}.".format(inp,
                chan, karma['net'], karma['pos'], karma['neg'], float(karma['pos']) / float(karma['pos'] + abs(karma['neg'])),
                upvoters or "None", downvoters or "None"))

