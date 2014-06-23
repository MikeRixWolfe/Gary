import re, sys, time
from util import hook, http

re_lineends = re.compile(r'[\r\n]*')


@hook.command
def python(inp):
    ".python <prog> - executes python code <prog>"
    try:
        res = http.get("http://eval.appspot.com/eval", statement=inp).splitlines()
    except Exception as e:
        return "Error: {}".format(e)
    if res:
        return (re_lineends.split(res[0])[0] if res[0] != 'Traceback (most recent call last):' else res[-1])


@hook.command(adminonly=True)
def ply(inp, bot=None, input=None, nick=None, db=None, chan=None):
    ".ply <prog> - Execute local python."
    try:
        time.sleep(.1)
        from cStringIO import StringIO

        buffer = StringIO()
        sys.stdout = buffer
        exec(inp)
        sys.stdout = sys.__stdout__

        return buffer.getvalue().strip() or "No output"
    except Exception as e:
        return "Python execution error: %" % e
