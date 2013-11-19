"""
karma.py: written by MikeFightsBears 2013
"""

from util import hook

def db_init(db):
    db.execute("create table if not exists karma(chan, word, karma,"
	" primary key(chan, word))")
    db.commit()
	
def get_karma(db, chan, word):
    row = db.execute("select karma from karma where chan=? and word=lower(?)",
        (chan, word)).fetchone()
    if row:
        return row[0]
    else:
        return 0

@hook.singlethread	
@hook.regex(r'([^ ^\(^(\)\+\+)^(\)--)]+((\+\+)|(--))|\([^\(^(\)\+\+$)^(\)--)]+\)((\+\+)|(--)))')
def karma_edit(inp, chan='', nick='', say=None, db=None):
    db_init(db)
    word = inp.group(1)[:-2].strip('() ')
    if word.lower() == nick.lower():
	say("Please do not karma yourself.")
    else:
	karma = get_karma(db, chan, word)
	delta = inp.group(1)[-2:].strip()
	if delta == "++":
	    karma = karma + 1
	elif delta == "--":
	    karma = karma - 1
        else:
	    karma = karma
	db.execute("insert or replace into karma(chan, word, karma)"
	    "values(?,?,?)", (chan, word.lower(), karma))
	db.commit()

@hook.command
def karma(inp, chan='', say=None, db=None, input=None):
    ".karma <word> - returns karma of <word>; <word>(+ +|- -) - increments or decrements karma of <word> (no space)"
    db_init(db)
    karma = get_karma(db, chan, input.msg[7:].strip('()? '))

    if karma:
        say("%s has %s karma" % (input.msg[7:].strip('()? '), karma))
    else:
        say("%s has neutral karma" % input.msg[7:].strip('()? '))
