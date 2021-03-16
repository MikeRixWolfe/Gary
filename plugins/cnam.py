from util import hook, http


@hook.api_key('everyoneapi')
@hook.command('cid')
@hook.command
def cnam(inp, api_key=None):
    """cnam <10 digit number> - Get CNAM information for a number via EveryoneAPI."""
    try:
        url = 'https://api.everyoneapi.com/v1/phone/{}'.format('+1' + inp[-10:])
        data = http.get_json(url, account_sid=api_key["account_sid"],
            auth_token=api_key["auth_token"],
            data="name,carrier,line_provider,location,linetype")['data']
    except Exception as e:
        return "EveryoneAPI error, please try again in a few minutes."

    out = [u"Caller ID info for {}".format(inp)]

    if data.get('name'):
        out.append(u"Name: {}".format(data['name']))

    if data.get('location', {}).get('city') or data.get('location', {}).get('state'):
        locs = [x for x in [data.get('location', {}).get('city'),
            data.get('location', {}).get('state')] if x != None]
        if locs:
            out.append(u"Location: {}".format(', '.join(locs)))

    if data.get('line_provider') and data['line_provider'].get('name'):
        out.append(u"Provider: {}".format(data['line_provider']['name']))

    if data.get('carrier', {}).get('name'):
        out.append(u"Carrier: {}".format(data['carrier']['name']))

    if data.get('linetype'):
        out.append(u"Type: {}".format(data['linetype']))

    if len(out) > 1:
        return u"; ".join(out)
    else:
        return "No caller ID info for {}".format(inp)

