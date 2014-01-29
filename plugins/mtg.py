'''
mtg.py - rewritten by MikeFightsBears 2013
'''

import re

from util import hook, http


@hook.command
def mtg(inp):
    ".mtg <name> - gets information about Magic the Gathering card <name>"

    url = 'http://magiccards.info/query?v=card&s=cname'
    h = http.get_html(url, q=inp)

    name = h.find('body/table/tr/td/span/a')
    if name is None:
        return "no cards found"
    card = name.getparent().getparent().getparent()

    type = card.find('td/p').text.replace('\n', '')

    # this is ugly
    text = http.html.tostring(card.xpath("//p[@class='ctext']/b")[0])
    text = text.replace('<br>', '$')
    text = http.html.fromstring(text).text_content()
    text = re.sub(r'(\w+\s*)\$+(\s*\w+)', r'\1. \2', text)
    text = text.replace('$', ' ')
    text = re.sub(r'\(.*?\)', '', text)  # strip parenthetical explanations
    text = re.sub(r'\.(\S)', r'. \1', text)  # fix spacing

    name.make_links_absolute(base_url=url)
    link = name.attrib['href']
    name = name.text_content().strip()
    type = type.strip()
    text = ' '.join(text.split())

    return (
        ' | '.join(
            (" ".join(name.split()),
             " ".join(type.split()),
             " ".join(text.split()),
             link))
    )
