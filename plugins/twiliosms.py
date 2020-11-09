import json
import re
import time
from json import dumps
from twilio.rest import Client
from util import hook, http, text, web


twilio_cache = None


def db_init(db):
    db.execute("create table if not exists phonebook(name, phonenumber, private,"
               "primary key(name))")
    db.commit()


def get_phonenumber(db, name):
    row = db.execute("select phonenumber, private from phonebook where name like ?",
        (name,)).fetchone()
    return row or (None, None)


def get_name(db, phoneNumber):
    row = db.execute("select name from phonebook where phonenumber like ?",
        (phoneNumber,)).fetchone()
    return row[0] if row else None


def cache_messages():
    global twilio_cache
    if twilio_cache is None:
        with open('persist/twilio_cache', 'r') as f:
            twilio_cache = [l.strip('\n') for l in f.readlines() if l.strip('\n')]


def log_and_cache(message):
    global twilio_cache
    twilio_cache.append(message['MessageSid'])
    with open('persist/twilio_cache', 'w') as f:
        f.writelines([l + '\n' for l in twilio_cache])


def outputsms(api_key, conn, bot, db, chan=None):
    global twilio_cache
    block = bot.config["sms"]["private"]
    messages = []
    _messages = http.get_json(bot.config["messages_url"].format(api_key['account_sid'], api_key['number']))

    for message in _messages:
        if message['MessageSid'] in twilio_cache:
            continue

        sender = message['From'][-10:]  # Force number to fit our model
        sender_nick = get_name(db, sender)
        if sender_nick and all(x not in block for x in [sender, sender_nick.lower()]) \
                and message['MessageSid'] not in [m['MessageSid'] for m in messages]:
            if message['MediaUrl']:
                media_uri = bot.config["gallery_url"].format(message['MessageSid'])
                message['out'] = u"<{}> [MMS] {} - {}".format(sender_nick,
                    web.try_googl(media_uri), message['Body'] or "Presented without comment.")
            else:
                message['out'] = u"<{}> {}".format(sender_nick, message['Body'])
            messages.append(message)

    for message in messages:
        conn.send(u"PRIVMSG {} :{}".format(chan or bot.config['sms']['output_channel'], message['out']))
        log_and_cache(message)  # Mark all as read
        time.sleep(1)

    return len(messages)


@hook.api_key('twilio')
@hook.command(modonly=True, autohelp=False)
def parsesms(inp, say='', api_key=None, chan=None, conn=None, bot=None, db=None):
    """parsesms - Force an SMS check from Twilio."""
    if not isinstance(api_key, dict) or any(key not in api_key for key in
            ('account_sid', 'auth_token', 'number')):
        return "Error: API keys not set."

    db_init(db)
    cache_messages()
    say("Checking for unread SMS...")

    sms_count = outputsms(api_key, conn, bot, db, chan)
    if sms_count:
        say("Processing {} message(s) complete.".format(sms_count))
    else:
        say("No new SMS found.")


@hook.api_key('twilio')
@hook.singlethread
@hook.event('JOIN')
def parseloop(paraml, nick='', api_key=None, conn=None, bot=None, db=None):
    if not isinstance(api_key, dict) or any(key not in api_key for key in
            ('account_sid', 'auth_token', 'number')):
        return "Error: API keys not set."

    db_init(db)
    cache_messages()
    if paraml[0] != bot.config['sms']['output_channel']:
        return

    time.sleep(1)  # Allow chan list time to update
    print(">>> u'Beginning SMS parse loop :{}'".format(paraml[0]))

    while paraml[0] in conn.channels:
        time.sleep(3)
        try:
            sms_count = outputsms(api_key, conn, bot, db)
            if sms_count:
                print(">>> u'Processing {} message(s) complete :{}'".format(sms_count, paraml[0]))
        except Exception as e:
            print(">>> u'Twilio loop error: {} :{}'".format(e, paraml[0]))
    print(">>> u'Ending SMS parse loop :{}'".format(paraml[0]))


@hook.api_key('twilio')
@hook.command
def sms(inp, nick='', chan='', user='', api_key=None, db=None, bot=None):
    """sms <nick> <message> - Sends a text message via Twilio."""
    if not isinstance(api_key, dict) or any(key not in api_key for key in
            ('account_sid', 'auth_token', 'number')):
        return "Error: API keys not set."

    if chan != bot.config['sms']['output_channel']:
        return

    db_init(db)
    block = bot.config["sms"]["private"]
    operands = inp.strip().split(' ', 1)

    if len(operands) < 2:
        return u"Please check your input and try again."
    recip = operands[0].lower().encode('ascii', 'ignore')
    text = u"<{}> {}".format(nick, operands[1])
    recip_number, private = get_phonenumber(db, recip)

    if not recip_number:
        return u"Sorry, I don't have that user in my phonebook."
    if any(x in block for x in [recip_number, recip.lower(), nick.lower(), user.lower()]):
        return u"I'm sorry {}, I'm afraid I can't do that.".format(nick)

    try:
        client = Client(api_key['account_sid'], api_key['auth_token'])
        msg = client.messages.create(to=recip_number, from_=api_key['number'], body=text)
        return "SMS sent."
    except TwilioRestException as e:
        return e.msg
    except Exception as e:
        print(e)
        return "Twilio API error, please try again in a few minutes."


@hook.api_key('twilio')
@hook.command(adminonly=True, autohelp=False)
def smsusage(inp, say=None, api_key=None):
    """smsusage - Get Twilio usage for the past 6 months."""
    try:
        client = Client(api_key['account_sid'], api_key['auth_token'])
        results = client.usage.records.monthly.list(category='sms')[:6]
        months = ["{month} ${0.price} ({0.count} messages)".format(item,
            month=time.strftime("%B", time.strptime(str(item.start_date), "%Y-%m-%d"))) for item in results]
        say("Usage by month: {}".format(", ".join(months)))
    except TwilioRestException as e:
        return e.msg
    except Exception as e:
        print(e)
        return "Twilio API error, please try again in a few minutes."


@hook.command
def phonebook(inp, chan='', nick='', user='', input=None, db=None, bot=None):
    """phonebook <nick|number|delete|private> - Gets a users phone number, or sets/deletes your phone number, or toggles private status."""
    db_init(db)
    block = bot.config["sms"]["private"]
    inp = inp.lower().strip().encode('ascii', 'ignore')

    if ' ' in inp:  # idiots
        return "This command takes a single parameter. Ex: 'phonebook 5556661234' or 'phonebook delete'."

    if inp.isdigit():
        inp = inp[-10:]
        if any(x in block for x in [inp, nick.lower(), user.lower()]): return "Nope."
        if len(inp) < 10:
            return "Please check your input and try again."
        db.execute("insert or replace into phonebook(name, phonenumber, private)"
                   "values(?, ?, ?)", (nick.lower(), inp, 0))
        db.commit()
        return "Number saved!"
    elif inp in ['delete', 'private']:
        phone_number, private = get_phonenumber(db, nick.lower())
        if phone_number:
            if inp == 'delete':
                if any(x in block for x in [nick.lower(), user.lower()]): return "Nope."
                db.execute("delete from phonebook where name = (?)", (nick.lower(),))
                db.commit()
                return "Your number has been removed from my phonebook."
            elif inp == 'private':
                if private:
                    db.execute("update phonebook set private = 0 where name = ?",
                        (nick.lower(),))
                    db.commit()
                    return "Your number is no longer private."
                else:
                    db.execute("update phonebook set private = 1 where name = ?",
                        (nick.lower(),))
                    db.commit()
                    return "Your number is now private."
        return "User does not have a registered phone number."
    else:
        phone_number, private = get_phonenumber(db, inp)
        if phone_number:
            if private:
                return "{}'s number is set to private.".format(inp).replace("s's", "s'")
            else:
                return "{}'s number is {}".format(inp, phone_number).replace("s's", "s'")
        else:
            return "User does not have a registered phone number."


@hook.command(adminonly=True)
def block(inp, nick='', conn=None, bot=None, say=None):
    """block <list|add|del> [contact|number] - Displays block or adds/dels contacts/numbers to/from block."""
    private = bot.config["sms"]["private"]
    inp = inp.lower().split()
    if len(inp) == 1 and inp[0] == 'list':
        if private:
            say("block sent via pm")
            conn.msg(nick, "block: {}".format(", ".join(private)))
        else:
            return "The block is currently empty."
    elif len(inp) == 2 and inp[0] in ['add', 'del']:
        contact = inp[1].strip('+: ').encode('ascii', 'ignore')
        if contact.isdigit():
            contact = contact[-10:]
        if inp[0] == 'add':
            if contact in private:
                return "{} is already blocked.".format(contact)
            else:
                private.append(contact)
                private.sort()
                json.dump(bot.config, open('config.json', 'w'), sort_keys=True, indent=2)
                return "{} has been blocked.".format(contact)
        else:
            if contact in private:
                private.remove(contact)
                private.sort()
                json.dump(bot.config, open('config.json', 'w'), sort_keys=True, indent=2)
                return "{} has been removed from the block.".format(contact)
            else:
                return "{} is not blocked.".format(contact)
    else:
        return block.__doc__

