import inspect
import json
import os


def save(conf):
    json.dump(conf, open('config', 'w'), sort_keys=True, indent=2)

if not os.path.exists('config'):
    open('config', 'w').write(inspect.cleandoc(
        r'''{
          "acls": {},
          "admins": [
            "bears"
          ],
          "api_keys": {
            "domainr": "",
            "everyoneapi": {
              "account_sid": "",
              "auth_token": ""
            },
            "giphy": "",
            "google": {
              "access": "",
              "cx": ""
            },
            "lastfm": "",
            "lastfm_secret": "",
            "mashery":
            {
              "consumer": "",
              "consumer_secret": ""
            },
            "rdio_key": "",
            "rdio_secret": "",
            "rottentomatoes": "",
            "steam_key": "",
            "tvdb": "",
            "twilio": {
              "account_sid": "",
              "auth_token": "",
              "number": ""
          },
            "twitter": {
              "access": "",
              "access_secret": "",
              "consumer": "",
              "consumer_secret": ""
            },
            "wolframalpha": "",
            "wordnik": "",
            "yahoo": {
              "consumer": "",
              "consumer_secret": ""
            }
          },
          "censored": [
            "DCC SEND",
            "\\0",
            "\\x01",
            "nigger"
          ],
          "connections": {
            "local": {
              "channels": [
                "#test"
              ],
              "nick": "Gary",
              "nickserv_password": "xxxx",
              "realname": "Gary",
              "server": "localhost",
              "user": "Gary"
            },
            "freenode": {
              "channels": [
                "#test"
              ],
              "nick": "Gary",
              "nickserv_password": "xxxx",
              "port": 8001,
              "realname": "Gary",
              "server": "irc.freenode.net",
              "user": "Gary"
            }
          },
        "disabled": [
            "beats",
            "cypher",
            "decypher",
            "gibberish"
          ],
          "sms": {
            "private": [
              "Gary"
            ]
          },
          "ignored": [],
          "muted": [],
          "moded": [],
          "rejoin": true,
          "restricted": [],
          "allowed": []
        }''') + '\n')


def config():
    # reload config from file if file has changed
    config_mtime = os.stat('config').st_mtime
    if bot._config_mtime != config_mtime:
        try:
            bot.config = json.load(open('config'))
            bot._config_mtime = config_mtime
        except ValueError as e:
            print('ERROR: malformed config!')
            print(e)


bot._config_mtime = 0
