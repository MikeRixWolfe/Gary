"""
sms.py written by MikeFightsBears September 2013
requires pygooglevoice
"""
import time, re, sys, BeautifulSoup, json
from util import hook, text
from googlevoice import Voice
from googlevoice.util import input

running_parseloop_threads = []

def db_init(db):
    db.execute("create table if not exists phonebook(name, phonenumber,"
                 "primary key(name))")
    db.execute("create table if not exists smslog(msgId,"
                 "primary key(msgId))")
    db.commit()


def get_phonenumber(db, name):
    row = db.execute("select phonenumber from phonebook where name like ?",
                (name,)).fetchone()
    if row:
        return row[0]
    else:
        return None


def get_name(db, phoneNumber):
    row = db.execute("select name from phonebook where phonenumber like ?",
                (phoneNumber,)).fetchone()
    if row:
        return row[0]
    else:
        return None


def check_smslog(db, msgId):
    row = db.execute("select msgId from smslog where msgId like ?",
                (msgId,)).fetchone()
    if row:
        return row[0]
    else:
        return None


def mark_as_read(db, msgId):
    db.execute("insert into smslog(msgId)"
            "values(?)", (msgId,))
    db.commit()
    return


def extractsms(htmlsms):
    """
    extractsms  --  extract SMS messages from BeautifulSoup tree of Google Voice SMS HTML.
    Output is a list of dictionaries, one per message.
    """
    msgitems = []                                       # accum message items here
    #   Extract all conversations by searching for a DIV with an ID at top level.
    tree = BeautifulSoup.BeautifulSoup(htmlsms)         # parse HTML into tree
    conversations = tree.findAll("div",attrs={"id" : True},recursive=False)
    for conversation in conversations :
        #   For each conversation, extract each row, which is one SMS message.
        rows = conversation.findAll(attrs={"class" : "gc-message-sms-row"})
        for row in rows :                               # for all rows
            #   For each row, which is one message, extract all the fields.
            msgitem = {"id" : conversation["id"]}       # tag this message with conversation ID
            spans = row.findAll("span",attrs={"class" : True}, recursive=False)
            for span in spans :                         # for all spans in row
                cl = span["class"].replace('gc-message-sms-', '')
                msgitem[cl] = (" ".join(span.findAll(text=True))).strip()   # put text in dict
            msgitems.append(msgitem)                    # add msg dictionary to list
    return msgitems


@hook.command()
def sms(inp, nick='', chan='', say='', input=None, db=None, bot=None):
    ".sms <10 digit number|name in phonebook> <message> - sends a text message to a specified number or recipient via Google Voice"
    if input.chan[0] != '#':
        return "Can only SMS from public channels to control abuse."
    db_init(db)
    voice = Voice()
    privatelist = bot.config["gvoice"]["private"]
    try:
        inp=inp.strip().decode('utf8','ignore')
    except:
        return "Error sending SMS; message contains unsupported characters"

    operands = inp.split(' ', 1)
    name_or_num = operands[0].strip()
    text = "<"+ nick + "> " + operands[1].strip()
        
    if len(name_or_num) == 10 and name_or_num.isdigit():
        phoneNumber = name_or_num
    else:
        num_from_db = get_phonenumber(db, name_or_num.lower())
        if num_from_db != None:
            phoneNumber = num_from_db
        else:
            return "Sorry, I don't have that user in my phonebook."

    if phoneNumber in privatelist:
        say("I'm sorry %s, I'm afraid I can't do that." % nick)
        return

    try:
        voice.login()
        voice.send_sms(phoneNumber, text)
        return "SMS sent"
    except:
        return "Google Voice API error, please try again in a few minutes."


@hook.command(adminonly=True)
def call(inp, say='', nick='', input=None, db=None, bot=None):
    ".call <10 digit number|user in phonebook> - calls specified <number|user> and connects the call to your number from .phonebook via Google Voice"
    db_init(db)
    privatelist = bot.config["gvoice"]["private"]
    forwardingNumber = get_phonenumber(db, nick)
    if forwardingNumber != None:
        voice = Voice()
        name_or_num = inp.strip(' ').decode('utf8', 'ignore')
        if not name_or_num.isdigit():
            outgoingNumber = get_phonenumber(db, name_or_num)
            if outgoingNumber == None:
                return "That user isn't in my phonebook."
        else:
            if len(name_or_num) == 10 and name_or_num.isdigit():
                outgoingNumber = name_or_num
            else:
                "Plese make sure the number is a 10 digit numeric."   
        if outgoingNumber in privatelist:
            say("I'm sorry %s, I'm afraid I caan't do that." % nick)
            return
        try:
            voice.login()
        except:
            return "Google Voice login error, please try again in a few minutes."
        voice.call(outgoingNumber, forwardingNumber)
        say("Calling %s from %s..." % (outgoingNumber, forwardingNumber))
    else:
        return "Your number needs to be in my phonebook to use this function"


#@hook.singlethread
#@hook.command(adminonly=True, autohelp=False)
@hook.event('JOIN')
def parseloop(inp, say='', conn=None, bot=None, db=None):
    server = "%s:%s" % (conn.server,conn.port)
    global running_parseloop_threads
    if server != "localhost:7666":
        return
    if len(running_parseloop_threads) > 0:
        print(">>> u'I am already parsing SMS for :%s'" % server)
        return
    else:
        running_parseloop_threads.append(server)
        print(">>> u'Beginning SMS parse loop for %s'" % server)
    db_init(db)
    privatelist = bot.config["gvoice"]["private"]
    voice = Voice()
    try:
        voice.login()
    except:
        print(">>> u'Error logging in to Google Voice :%s'" % server)
        return
    try:    
        while voice.sms():
            print(">>> u'Checking for unread sms :%s'" % server)
            messagecounter=0
            for message in extractsms(voice.sms.html):
                if check_smslog(db, message['id']) == None and message['from'][:-1] not in privatelist:
                    messagecounter=messagecounter+1
                    number = message['from'][2:-1] #slice off "+1" and ":"
                    recip_nick = get_name(db, number)
                    if recip_nick != None:
                        text="<"+recip_nick+"> "+message['text']
                        for chn in conn.channels:
                            out = "PRIVMSG {} :{}".format(chn, text)
                            conn.send(out)
                        mark_as_read(db, str(message['id']))
                    else:
                        text="<"+number+"> "+message['text']
                        for chn in conn.channels:
                            out = "PRIVMSG {} :{}".format(chn, text)
                            conn.send(out)
                        mark_as_read(db, str(message['id']))
            if messagecounter == 0:
               print(">>> u'No new SMS found :%s'" % server)
            elif messagecounter == 1:
                print(">>> u'Outputting "+ str(messagecounter) +" message complete :%s'" % server)
            else:
                print(">>> u'Outputting "+ str(messagecounter) +" messages complete :%s'" % server)
            time.sleep(60)
    except:
        print(">>> u'Error parsing data from Google Voice :%s'" % server)
        #return
        #running_parseloop_threads.remove(server)
        # state error in public channels rather than PMs so non admins know the loop is down
        #for chan in conn.channels:
        #    notified_admins = ", ".join(bot.config["admins"])
        #    conn.send("PRIVMSG {} :{}".format(chn, "%s: My SMS parse loop died; please restart parseloop :%s" % (notified_admins, server)))
        #break
        

@hook.command(adminonly=False, autohelp=False)
def parsesms(inp, say='', conn=None, bot=None, db=None):
        ".parsesms - force an sms check from Google Voice"
        db_init(db)
        privatelist = bot.config["gvoice"]["private"]
        voice = Voice()
        try:
            voice.login()
        except:
            say(">>> u'Error logging in to Google Voice, please try again in a few minutes.'")
            return
        try:
            voice.sms()
        except:
            say(">>> u'Error parsing data from Google Voice'")
            return
        say(">>> u'Checking for unread sms'")
        messagecounter=0
        for message in extractsms(voice.sms.html):
            if check_smslog(db, message['id']) == None and message['from'][:-1] not in privatelist:
                messagecounter=messagecounter+1
                number = message['from'][2:-1] #slice off "+1" and ":"
                recip_nick = get_name(db, number)
                if recip_nick != None:
                    text="<"+recip_nick+"> "+message['text']
                    for chn in conn.channels:
                        out = "PRIVMSG {} :{}".format(chn, text)
                        conn.send(out)
                    mark_as_read(db, str(message['id']))
                else:
                    text="<"+number+"> "+message['text']
                    for chn in conn.channels:
                        out = "PRIVMSG {} :{}".format(chn, text)
                        conn.send(out)
                    mark_as_read(db, str(message['id']))
        if messagecounter == 0:
            say(">>> u'No new SMS found'")
        elif messagecounter == 1:
            say(">>> u'Outputting "+ str(messagecounter) +" message complete'")
        else:
            say(">>> u'Outputting "+ str(messagecounter) +" messages complete'")


@hook.command
def phonebook(inp, nick='', input=None, db=None, bot=None):
    ".phonebook <name|10 digit number|delete> - gets a users phone number, or sets/deletes your phone number"
    db_init(db)
    privatelist = bot.config["gvoice"]["private"]
    name_or_num = inp.strip()
    if name_or_num in privatelist:
        return "Nope."
    if name_or_num.isdigit():
        if len(name_or_num) == 10:
            db.execute("insert or replace into phonebook(name, phonenumber)"
                "values(?, ?)", (nick.lower(), name_or_num))
            db.commit()
            return "Number saved!"
        else:
            return "Please be sure your are inputting a 10 digit number."
    if name_or_num == 'delete':
        db.execute("delete from phonebook where "
            "name = (?)", (nick.lower(),))
        return "Your number has been removed from my phonebook."
    else:
        num_from_db = get_phonenumber(db, name_or_num.lower())
        if num_from_db != None:
            return name_or_num + "'s number is " + num_from_db
        else:
            return "User does not have a registered phone number"


@hook.command(adminonly=True, autohelp=False)
def privatecontacts(inp, notice=None, bot=None, say=None):
    """.privateContacts - Lists private contacts."""
    privatelist = bot.config["gvoice"]["private"]
    if privatelist:
        say("Private contacts: %s" % format(", ".join(privatelist)))
    else:
        say("You currently have no private contacts.")
    return


@hook.command(adminonly=True)
def add_privatecontact(inp, say=None, notice=None, bot=None, config=None):
    """.add_privateContact <number|contact> - adds <number|contact> to private contact list."""
    target = inp.strip()
    privatelist = bot.config["gvoice"]["private"]
    if target in privatelist:
        say("%s is already a private contact." % format(target))
    else:
        admins = bot.config.get('admins', [])
        say("%s has been added as a private contact." % format(target))
        privatelist.append(target)
        privatelist.sort()
        json.dump(bot.config, open('config', 'w'), sort_keys=True, indent=2)
    return


@hook.command(adminonly=True)
def remove_privatecontact(inp, say=None, notice=None, bot=None, config=None):
    """.remove_privateContact <number|contact> - removes <number|contact> from private contact list."""
    target = inp.strip()
    privatelist = bot.config["gvoice"]["private"]
    if target in privatelist:
        say("%s has been removed as a private contact." % format(target))
        privatelist.remove(target)
        privatelist.sort()
        json.dump(bot.config, open('config', 'w'), sort_keys=True, indent=2)
    else:
        say("%s is not a private contact." % format(target))
    return
