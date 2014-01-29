import urllib
import urllib2
import re
from util import hook
from lxml import etree, html


def get_response(code):
    url = "http://codepad.org/"

    parameters = {
        "lang": "Ruby",
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


@hook.command
def ruby(inp, say=None):
    '''.rb / .ruby <code> - Executes Ruby code.'''

    code = inp.split(" ")[0:]
    code = " ".join(code)

    response = get_response(code)
    document, url = response
    output = parse_html(document)

    return output[-1].encode("ascii", "ignore")
