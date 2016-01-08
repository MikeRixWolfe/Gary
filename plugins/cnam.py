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
        print e.msg
        return "EveryoneAPI error, please try again in a few minutes."

    out = [u"Caller ID info for {number}".format(**data)]

    if data['data'].get('expanded_name', None) or data['data'].get('cnam', None):
        if data['data'].get('expanded_name', None):
            out.append(u"Name: {}".format(
                ' '.join([data['data'].get('expanded_name', {}).get('first', None),
                data['data'].get('expanded_name', {}).get('last', None)])))
        else:
            out.append(u"Name: {}".format(data['data']['cnam']))

    if data.get('type', None) and data['data'].get('linetype', None):
        out.append(u"Type: {}".format(', '.join([data.get('type', None),
        data['data'].get('linetype', None)])))

    if data['data'].get('location', {}).get('city', None) and \
            data['data'].get('location', {}).get('state', None):
        out.append(u"Location: {}".format(', '.join([
            data['data'].get('location', {}).get('city', None),
            data['data'].get('location', {}).get('state', None)])))

    if data['data'].get('carrier', {}).get('name', None):
        out.append(u"Carrier: {}".format(data['data']['carrier']['name']))

    return u"; ".join(out)

