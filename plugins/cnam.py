from util import hook, http


@hook.api_key('everyoneapi')
@hook.command
def cnam(inp, api_key=None):
    """.cnam <10 digit number> - Get CNAM information for a number via EveryoneAPI."""
    url = 'https://api.everyoneapi.com/v1/phone/{}'.format(inp)

    try:
        data = http.get_json(url, account_sid=api_key["account_sid"],
            auth_token=api_key["auth_token"],
            data="name,carrier,location,linetype,cnam")
    except Exception as e:
        return "EveryoneAPI error, please try again in a few minutes."

    out = [u"Caller ID info for {number}".format(**data)]

    if data['data'].get('expanded_name', None) or data['data'].get('cnam', None):
        if data['data'].get('expanded_name', None):
            names = [x for x in [data['data'].get('expanded_name', {}).get('first', None),
                data['data'].get('expanded_name', {}).get('last', None)] if x != None]
            if names:
                out.append(u"Name: {}".format(' '.join(names).strip()))
        else:
            if data['data']['cnam'].lower() != 'unknown':
                out.append(u"Name: {}".format(data['data']['cnam']).strip())

    if data.get('type', None) or data['data'].get('linetype', None):
        types = [x for x in [data.get('type', 'unknown'),
            data['data'].get('linetype', 'unknown')] if x != 'unknown']
        if types:
            out.append(u"Type: {}".format(', '.join(types)))

    if data['data'].get('location', {}).get('city', None) or data['data'].get('location', {}).get('state', None):
        locs = [x for x in [data['data'].get('location', {}).get('city', None),
            data['data'].get('location', {}).get('state', None)] if x != None]
        if locs:
            out.append(u"Location: {}".format(', '.join(locs)))

    if data['data'].get('carrier', {}).get('name', None):
        out.append(u"Carrier: {}".format(data['data']['carrier']['name']))

    if out:
        return u"; ".join(out)
    else:
        return "No caller ID info for {}".format(inp)

