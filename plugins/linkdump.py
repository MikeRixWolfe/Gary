import re
from datetime import datetime
from util import hook, web

html_re = r'https?://[^\s<>"]+|www\.[^\s<>"]+'


@hook.command(autohelp=False)
def linkdump(inp, chan="", say="", db=None):
    """.linkdump - Gets today's links dumped in channel."""
    today = datetime.today()
    period = float(datetime(today.year, today.month, today.day).strftime('%s'))
    rows = db.execute("select nick, msg, time from log where uts >= ? and chan = ? and " \
        "(msg like '%http://%' or msg like '%https://%')", (period, chan)).fetchall()

    if not rows:
        return "No links yet today (beginning with 'http')"

    links = ["via %s [%s]: %s" % (row[0], re.search(r'(\d+\:\d+:\d+)', row[2]).group(0),
        re.search(html_re, row[1]).group(0)) for row in rows]
    say("Today's link dump: " + web.haste('\n'.join(links), 'txt'))


