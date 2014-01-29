import re

from util import hook, http
"import usertracking"
"import sys"

re_lineends = re.compile(r'[\r\n]*')


@hook.command
def python(inp):
    ".python <prog> - executes python code <prog>"

    res = http.get("http://eval.appspot.com/eval", statement=inp).splitlines()
    #print(res)
    if len(res) == 0:
        return
    res[0] = re_lineends.split(res[0])[0]
    if not res[0] == 'Traceback (most recent call last):':
        return res[0].decode('utf8', 'ignore')
    else:
        return res[-1].decode('utf8', 'ignore')


@hook.command(adminonly=True)
def py(inp, bot=None, input=None, nick=None, db=None, chan=None):
    ".py <prog> - execute local python"
    arguments = inp.split(" ")
    exec(" ".join(arguments[1:]))
