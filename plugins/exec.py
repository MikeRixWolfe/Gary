import re
import subprocess
from lxml import etree
from urllib import urlencode
from util import hook, http


@hook.command('py')
@hook.command
def python(inp, say=None):
    """.py[thon] <code> - Executes Python code on the Google App Engine."""
    try:
        heads = {'Referer': 'http://codepad.org/'}
        params = urlencode({"lang": "Python", "code": inp, "run": "True", "submit": "Submit"})
        document = http.get("http://codepad.org/", post_data=params, headers=heads, get_method="POST")
        html = etree.HTML(document)
        out = html.xpath('//div[@class="code"][2]//td[2]//pre//text()')
    except Exception as e:
        return e

    return re.sub(" +", " ", " ".join(out).replace("\n", " ")).strip() if out else "No output."


@hook.command('rb')
@hook.command
def ruby(inp, say=None):
    """.rb/.ruby <code> - Executes Ruby code via Codepad.org."""
    try:
        heads = {'Referer': 'http://codepad.org/'}
        params = urlencode({"lang": "Ruby", "code": inp, "run": "True", "submit": "Submit"})
        document = http.get("http://codepad.org/", post_data=params, headers=heads, get_method="POST")
        html = etree.HTML(document)
        out = html.xpath('//div[@class="code"][2]//td[2]//pre//text()')
    except Exception as e:
        return e

    return re.sub(" +", " ", " ".join(out).replace("\n", " ")).strip() if out else "No output."


@hook.command(adminonly=True)
def ply(inp):
    """.ply <prog> - Execute local Python."""
    try:
        out = subprocess.check_output(["python", "-c", inp], stderr=subprocess.STDOUT)
        return re.sub(" +", " ", out.replace("\n", " ")).strip() if out else "No output."
    except subprocess.CalledProcessError as e:
        return e.output

