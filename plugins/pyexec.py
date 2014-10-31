import re
import sys
import time
import urllib
import urllib2
from util import hook, http
from lxml import etree, html


def get_response(code):
    url = "http://codepad.org/"

    parameters = {
        "lang": "Python",
        "code": code,
        "run": "True",
        "submit": "Submit"
    }

    request = urllib2.Request(url, urllib.urlencode(parameters))
    response = urllib2.urlopen(request).read()
    response_url = urllib2.urlopen(request).geturl()

    return [response, response_url]


def parse_html(document):
    html = etree.HTML(document)
    output = html.xpath('//div[@class="code"][2]//pre//text()')
    return output


@hook.command('py')
@hook.command
def python(inp, say=None):
    """.py[thon] <code> - Executes Python code via Codepad.org."""

    code = inp.split(" ")[0:]
    code = " ".join(code)

    try:
        response = get_response(code)
        document, url = response
        output = parse_html(document)
    except Exception as e:
        return e

    if output == []:
        return "No output"

    return output[-1].encode("ascii", "ignore")


@hook.command(adminonly=True)
def ply(inp, bot=None, input=None, nick=None, db=None, chan=None):
    """.ply <prog> - Execute local Python."""
    try:
        time.sleep(.1)
        from cStringIO import StringIO

        buffer = StringIO()
        sys.stdout = buffer
        exec(inp)
        sys.stdout = sys.__stdout__

        return buffer.getvalue().strip() or "No output"
    except Exception as e:
        return "Python execution error: %s" % e
