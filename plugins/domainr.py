from util import hook, http, web


@hook.command
def domainr(inp, say=''):
    """.domainr <domain> - Use domai.nr's API to search for a domain, and similar domains."""
    try:
        data = http.get_json('http://domainr.com/api/json/search?q=' + inp)
    except (http.URLError, http.HTTPError) as e:
        return "Unable to get data for some reason. Try again later."
    if data['query'] == "":
        return "An error occurrred: {status} - {message}".format(**data['error'])
    domains = []
    for domain in data['results']:
        domains.append(("\x034" if domain['availability'] == "taken" else (
            "\x033" if domain['availability'] == "available" else "\x038")) + domain['domain'] + "\x0f" + domain['path'])
    say("Domains: {} - {}".format(", ".join(domains), web.try_googl("http://domainr.com/?q=" + inp.strip())))
