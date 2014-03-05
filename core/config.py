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
            "giphy": "",
            "google": "",
            "googletranslate": "",
            "lastfm": "",
            "lastfm_secret": "",
            "rdio_key": "",
            "rdio_secret": "",
            "rottentomatoes": "",
            "steam_key": "",
            "twitter": {
              "access": "",
              "access_secret": "",
              "consumer": "",
              "consumer_secret": ""
            },
            "wolframalpha": "",
            "yahoo": {
              "consumer": "",
              "consumer_secret": ""
            }
          },
          "censored_strings": [
            "DCC SEND",
            "\\0",
            "\\x01",
            "nigger"
          ],
          "connections": {
            "bearsircd": {
              "channels": [
                "#test"
              ],
              "nick": "Gary",
              "nickserv_password": "xxxx",
              "realname": "Gary",
              "server": "localhost",
              "user": "Gary"
            },
            "dot": {
              "channels": [
                "#geekboy"
              ],
              "nick": "Gary",
              "nickserv_password": "xxxx",
              "port": 7666,
              "realname": "Gary",
              "server": "localhost",
              "user": "Gary"
            }
          },
        "disabled": [
            "beats",
            "cron.py",
            "cypher",
            "decypher",
            "gibberish"
          ],
          "gvoice": {
            "private": [
              "Gary"
            ]
          },
          "ignored": [],
          "muted": [],
          "opers": [],
        "rejoin": true,
          "restrictedmode": [],
          "voice": []
        }''') + '\n')


def config():
    # reload config from file if file has changed
    config_mtime = os.stat('config').st_mtime
    if bot._config_mtime != config_mtime:
        try:
            bot.config = json.load(open('config'))
            bot._config_mtime = config_mtime
        except ValueError, e:
            print 'ERROR: malformed config!', e


bot._config_mtime = 0
