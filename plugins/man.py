"""
man.py - written by MikeFigthtsBears 2014
"""

import re, os
from util import hook, web, http, text


base_url="http://man.he.net/?topic={}&section={}"

def get_system_manpage(command):
    out = os.popen("man -P cat {}".format(command)).read().strip()
    if len(out)>1:
        return out
    else:
        return None


@hook.command
def man(inp, say=''):
    '''.man <command> [section] - Returns man page for specified command, section defaults to 1 if not specified.'''
    raw = inp.split()
    
    command = raw[0]
    if len(raw) == 2 and raw[1].isdigit():
        page = raw[1]
    else:
        page = "1"
  
    try:
        manpage = str(http.get_html(base_url, topic=command, section=page))
        # If not specified man page
        if re.match(r'.+(\>No matches for ").+', manpage):
            page = "all"
            manpage = str(http.get_html(base_url, topic=command, section=page))
        # If man page exists for command
        if not re.match(r'.+(\>No matches for ").+', manpage) and 1==2:
            if page != "all":
                say("{} - {}({})".format(web.try_isgd(base_url.format(command, page)), command, page))
            else:
                say("{} - {}({}) (No section {})".format((web.try_isgd(base_url.format(command, page)), command, page, raw[1])))
        else:
            system_manpage = get_system_manpage(command)
            if system_manpage:
                haste_url = web.haste(system_manpage, ext='txt')
                isgd_url = web.try_isgd(haste_url)
                say("{} - {}".format(isgd_url, command, page))
            else:
                return "There is no man page for {}.".format(command)
    except Exception as e:#(http.HTTPError, http.URLError) as e:
        print(">>> u'HTTP Error: {}'".format(e))
        return "HTTP Error, please try again in a few minutes."

# man -P cat grep | grep -A 1 -e  "-mmap"
