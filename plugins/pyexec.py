import re, sys
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


#@hook.command(adminonly=True)
def ply(inp, bot=None, input=None, nick=None, db=None, chan=None):
    "execute local python - only admins can use this"
    from cStringIO import StringIO
    old_stdout = sys.stdout
    redirected_output = sys.stdout = StringIO()
    exec(inp)
    sys.stdout = old_stdout

    return redirected_output.getvalue()
