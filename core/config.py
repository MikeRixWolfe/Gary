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
          "allowed": [],
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
            "imgur": {
              "client_id": "",
              "client_secret": ""
            },
            "lastfm": "",
            "mashery": {
              "consumer": "",
              "consumer_secret": ""
            },
            "rottentomatoes": "",
            "steam_key": "",
            "tvdb": "",
            "twitter": {
              "access": "",
              "access_secret": "",
              "consumer": "",
              "consumer_secret": ""
            },
            "wolframalpha": "",
            "wordnik": "",
            "wunder": "",
            "yahoo": {
              "access": "",
              "access_secret": "",
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
          "channels_only": false,
          "connections": {
            "localhost": {
              "channels": [
                #test
              ],
              "nick": "Gary",
              "nickserv_password": "",
              "port": 6667,
              "realname": "Gary",
              "server": "localhost",
              "user": "Gary2"
            },
            "freenode": {
              "channels": [
                #test
              ],
              "nick": "Gary",
              "nickserv_password": "",
              "port": 6667,
              "realname": "Gary",
              "server": "irc.freenode.net",
              "user": "Gary2"
            }
          },
          "disabled": [
            "chatlog.py",
            "cron.py",
            "factoids.py",
            "gex",
            "gif.py",
            "karma.py",
            "shorten",
            "slap",
            "stockhistory",
            "topartist",
            "topfriend",
            "toptrack",
            "twitterloop",
            "ud",
            "wotd"
          ],
          "ignored": [],
          "moded": [],
          "muted": [],
          "rejoin": true,
          "restricted": [],
          "suggestions": true
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
