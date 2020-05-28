import inspect
import json
import os


def save(conf):
    json.dump(conf, open('config.json', 'w'), sort_keys=True, indent=2)

if not os.path.exists('config.json'):
    raise Exception("ERROR: no config file, rename default.config.json to config.json and enter info")

def config():
    # reload config from file if file has changed
    config_mtime = os.stat('config.json').st_mtime
    if bot._config_mtime != config_mtime:
        try:
            bot.config = json.load(open('config.json'))
            bot._config_mtime = config_mtime
        except ValueError as e:
            print('ERROR: malformed config!')
            print(e)


bot._config_mtime = 0
