from util import hook, http


@hook.api_key('everyoneapi')
@hook.command('cid')
@hook.command
def cnam(inp, api_key=None):
    """cnam <10 digit number> - Get CNAM information for a number via OpenCNAM & EveryoneAPI."""
    try:
        url = 'https://api.everyoneapi.com/v1/phone/{}'.format(inp)
        data = http.get_json(url, account_sid=api_key["account_sid"],
            auth_token=api_key["auth_token"],
            data="line_provider,location,linetype")['data']
    except Exception as e:
        return "EveryoneAPI error, please try again in a few minutes."

    try:
        url = 'https://api.opencnam.com/v3/phone/{}'.format(inp)
        data2 = http.get_json(url, account_sid=api_key["account_sid"],
            auth_token=api_key["auth_token"],
            format="json")
    except Exception as e:
        return "OpenCNAM error, please try again in a few minutes."

    data.update(data2)
    out = [u"Caller ID info for {number}".format(**data)]

    # name or wire center
    if data.get('name'):
        out.append(u"Name: {}".format(data['name']))

    # rate center
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

