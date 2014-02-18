"""
sms.py written by MikeFightsBears September 2013
requires pygooglevoice
"""

import re
import sys
import time
import json
import BeautifulSoup
import googlevoice.util
from util import hook, text
from googlevoice import Voice


def db_init(db):
    db.execute("create table if not exists phonebook(name, phonenumber,"
               "primary key(name))")
    db.execute("create table if not exists smslog(id, sender, text, time,"
               "primary key(id, sender, text, time))")
    db.commit()


def get_phonenumber(db, name):
    row = db.execute("select phonenumber from phonebook where name like ?",
        (name,)).fetchone()
    return (row[0] if row else None)


def get_name(db, phoneNumber):
    row = db.execute("select name from phonebook where phonenumber like ?",
        (phoneNumber,)).fetchone()
    return (row[0] if row else None)


def check_smslog(db, msg):
    row = db.execute(
        "select * from smslog where id like ? and sender like ? and  text like ? and time like ?",
        (msg['id'], msg['from'], msg['text'], msg['time'])).fetchone()
    return (row[0] if row else None)


def mark_as_read(db, msg):
    db.execute("insert into smslog(id, sender, text, time) values (?,?,?,?)",
        (msg['id'], msg['from'], msg['text'], msg['time']))
    db.commit()


def extractsms(htmlsms):
    """
    extractsms  --  extract SMS messages from BS4 tree of Google Voice SMS HTML
    Output is a list of dictionaries, one per message.
    """
    msgitems = []  # accum message items here
    # Extract all conversations by searching for a DIV with an ID at top level.
    tree = BeautifulSoup.BeautifulSoup(htmlsms)   # parse HTML into tree
    conversations = tree.findAll("div", attrs={"id": True}, recursive=False)
    for conversation in conversations:
        #   For each conversation, extract each row, which is one SMS message.
        rows = conversation.findAll(attrs={"class": "gc-message-sms-row"})
        for row in rows:  # for all rows
            #   For each row, which is one message, extract all the fields.
            msgitem = {"id": conversation["id"]}  # tag msg with ID
            spans = row.findAll("span", attrs={"class": True},
                                recursive=False)
            for span in spans:  # for all spans in row
                cl = span["class"].replace('gc-message-sms-', '')
                # put text in dict
                msgitem[cl] = (" ".join(span.findAll(text=True))).strip()
            msgitems.append(msgitem)  # add msg dictionary to list
    return msgitems


def outputsms(voice, conn, bot, db):
    privatelist = bot.config["gvoice"]["private"]
    if not voice.special: voice.login()
    voice.sms()
    messages = []
    for message in extractsms(voice.sms.html):
        recip = message['from'].strip('+: ')
        if recip.isdigit():
            recip = recip[-10:]
        if recip != 'Me' and recip not in privatelist and not check_smslog(db, message):
            recip_nick = get_name(db, recip)
            message['out'] = "<{}> {}".format(
                recip_nick or recip, message['text'])
            messages.append(message)
    for message in messages:
        for chan in conn.channels:
            conn.send("PRIVMSG {} :{}".format(chan, message['out']))
        mark_as_read(db, message)
    return voice, len(messages)


@hook.command(adminonly=False, autohelp=False)
def parsesms(inp, say='', conn=None, bot=None, db=None):
    ".parsesms - force an sms check from Google Voice"
    db_init(db)
    voice = Voice()
    say("Checking for unread SMS...")
    try:
        voice, sms_count = outputsms(voice, conn, bot, db)
        if sms_count:
            say("Outputting {} message(s) complete.".format(sms_count))
        else:
            say("No new SMS found.")
    except googlevoice.util.LoginError:
        say("Error logging in to Google Voice; please try again in a few minutes.")
    except googlevoice.util.ParsingError:
        say("Error parsing data from Google Voice; please try again in a few minutes.")
    except:
        say("Ouch! I've encountered an unexpected error (and it hurt).")


@hook.singlethread
@hook.event('JOIN')
def parseloop(paraml, nick='', conn=None, bot=None, db=None):
    db_init(db)
    server = "%s:%s" % (conn.server, conn.port)
    if server != "localhost:7666" or paraml[0] != "#geekboy":
        return
    voice = Voice()
    print(">>> u'Beginning SMS parse loop for %s'" % server)
    while True:
        time.sleep(90)
        try:
            if not voice: voice = Voice()
            voice, sms_count = outputsms(voice, conn, bot, db)
            if sms_count:
                print(">>> u'Outputting {} message(s) complete :{}'".format(sms_count, server))
        except googlevoice.util.LoginError:
            print(">>> u'Google Voice login error :{}'".format(server))
            voice = None
        except googlevoice.util.ParsingError:
            print(">>> u'Google Voice parse error :{}'".format(server))
            voice = None
        except Exception as e:
            print(">>> u'Google Voice error: {} :{}'".format(e, server))


@hook.command()
def sms(inp, nick='', chan='', db=None, bot=None):
    ".sms <10 digit number|name in phonebook> <message> - sends a text message to a specified number or recipient via Google Voice"
    if chan[0] != '#':
        return "Can only SMS from public channels to control abuse."
    db_init(db)
    voice = Voice()
    privatelist = bot.config["gvoice"]["private"]
    inp = inp.strip().encode('ascii', 'ignore')
    operands = inp.split(' ', 1)
    if len(operands) < 2:
        return "Please check your input and try again."
    recip = operands[0].strip()
    text = "<" + nick + "> " + operands[1].strip()
    if recip.isdigit():
        phoneNumber = recip[-10:]
    else:
        recip_number = get_phonenumber(db, recip.lower())
        if recip_number:
            phoneNumber = recip_number
        else:
            return "Sorry, I don't have that user in my phonebook."
    if "+1" + phoneNumber[-10:] in privatelist or phoneNumber in privatelist:
        return "I'm sorry %s, I'm afraid I can't do that." % nick
    try:
        voice.login()
        voice.send_sms(phoneNumber, text)
        return "SMS sent"
    except:
        return "Google Voice API error, please try again in a few minutes."


@hook.command(adminonly=True)
def call(inp, say='', nick='', db=None, bot=None):
    ".call <number|nick> - calls specified <number|nick> and connects the call to your number from .phonebook via Google Voice"
    db_init(db)
    forwardingNumber = get_phonenumber(db, nick)
    if not forwardingNumber:
        return "Your number needs to be in my phonebook to use this function."
    voice = Voice()
    privatelist = bot.config["gvoice"]["private"]
    recip = inp.strip().encode('ascii', 'ignore')
    if recip.isdigit():
        outgoingNumber = recip[-10]
    else:
        outgoingNumber = get_phonenumber(db, recip)
        if not outgoingNumber:
            return "That user isn't in my phonebook."
    if outgoingNumber in privatelist:
        return "I'm sorry, I'm afraid I can't do that."
    try:
        voice.login()
        voice.call(outgoingNumber, forwardingNumber)
        say("Calling %s from %s..." % (outgoingNumber, forwardingNumber))
        time.sleep(30)
        voice.cancel(outgoingNumber, forwardingNumber)
    except:
        return "Google Voice API error, please try again in a few minutes."


@hook.command
def phonebook(inp, nick='', input=None, db=None, bot=None):
    ".phonebook <nick|number|delete> - gets a users phone number, or sets/deletes your phone number"
    db_init(db)
    privatelist = bot.config["gvoice"]["private"]
    recip = inp.strip().encode('ascii', 'ignore')
    if recip in privatelist:
        return "Nope."
    if recip.isdigit():
        if len(recip) < 10:
            return "Please check your input and try again."
        db.execute("insert or replace into phonebook(name, phonenumber)"
                   "values(?, ?)", (nick.lower(), recip[-10:]))
        db.commit()
        return "Number saved!"
    elif recip == 'delete':
        db.execute("delete from phonebook where name = (?)", (nick.lower(),))
        db.commit()
        return "Your number has been removed from my phonebook."
    else:
        recip_number = get_phonenumber(db, recip.lower())
        if recip_number is not None:
            return recip + "'s number is " + recip_number
        else:
            return "User does not have a registered phone number."


@hook.command(adminonly=True, autohelp=False)
def privatecontacts(inp, bot=None, say=None):
    """.privateContacts - Lists private contacts."""
    privatelist = bot.config["gvoice"]["private"]
    if privatelist:
        say("Private contacts: %s" % format(", ".join(privatelist)))
    else:
        return "You currently have no private contacts."


@hook.command(adminonly=True)
def add_privatecontact(inp, bot=None):
    """.add_privateContact <number|contact> - adds <number|contact> to private contact list."""
    contact = inp.strip('+: ').encode('ascii', 'ignore')
    privatelist = bot.config["gvoice"]["private"]
    if contact.isdigit():  # Format number to Google Voice Format
        contact = "+1" + contact[-10:]
    if contact in privatelist:
        return "%s is already a private contact." % format(contact)
    else:
        privatelist.append(contact)
        privatelist.sort()
        json.dump(bot.config, open('config', 'w'), sort_keys=True, indent=2)
        return "%s has been added as a private contact." % format(contact)


@hook.command(adminonly=True)
def remove_privatecontact(inp, bot=None):
    """.remove_privateContact <number|contact> - removes <number|contact> from private contact list."""
    contact = inp.strip('+: ').encode('ascii', 'ignore')
    privatelist = bot.config["gvoice"]["private"]
    if contact.isdigit():  # Format number to Google Voice Format
        contact = "+1" + contact[-10:]
    if contact in privatelist:
        privatelist.remove(contact)
        privatelist.sort()
        json.dump(bot.config, open('config', 'w'), sort_keys=True, indent=2)
        return "%s has been removed as a private contact." % format(contact)
    else:
        return "%s is not a private contact." % format(contact)
