import inspect
import json
import os


def save(conf):
    json.dump(conf, open('config', 'w'), sort_keys=True, indent=2)

if not os.path.exists('config'):
    open('config', 'w').write(inspect.cleandoc(
        r'''
        {
          "acls": {},
          "admins": [
            "bears"
          ],
          "api_keys": {
            "google": "",
            "googletranslate": "",
            "lastfm": "",
            "lastfm_secret": "",
            "rdio_key": "",
            "rdio_secret": "",
            "rottentomatoes": "",
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
            "local irc 1": {
              "channels": [
                "#geekboy"
              ],
              "nick": "Gary",
              "nickserv_password": "2secret4you",
              "port": 7666,
              "realname": "Gary",
              "server": "localhost",
              "user": "Gary"
            },
            "local irc 2": {
              "channels": [
                "#geekboy"
              ],
              "nick": "Gary",
              "nickserv_password": "2secret4you",
              "realname": "Gary",
              "server": "localhost",
              "user": "Gary"
            }
          },
          "disabled_commands": [
            "get_version"
          ],
          "disabled_plugins": [
            "readtitle"
          ],
          "gvoice": {
            "private": [
              "Me"
            ]
          },    
          "ignored": [
            "geekboy"
          ],
          "muted": [],
          "opers": [],
          "restrictedmode": []
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
