"""
blaze.py: written by MikeFightsBears... blaze it!
"""

import time
from util import hook

timestamp_format = '%I:%M'

def localtime(format):
    return time.strftime(format, time.localtime())

@hook.event('JOIN')
def blaze(inp, say=''):
    while True:
        timestamp = localtime(timestamp_format)
        if timestamp == '03:17': # my IRC server is in  a different time zone and off by 3 minutes, dont  judge me lol
            say("4:20 BLAZE IT!")
        time.sleep(60)
