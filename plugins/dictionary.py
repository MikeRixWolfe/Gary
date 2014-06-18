import re

from util import hook, http


@hook.command('ud')
@hook.command
def urban(inp):
    '''.ud/.urban <phrase> - looks up <phrase> on urbandictionary.com'''
    url = 'http://www.urbandictionary.com/iphone/search/define'
    referer = 'http://m.urbandictionary.com'
    try:
        page = http.get_json(url, term=inp, headers={'Referer': referer})
        defs = page['list']
    except:
        return "Error reading the Urban Dictionary API; please try again later.."

    if page['result_type'] == 'no_results':
        return 'not found.'

    out = defs[0]['word'] + ': ' + defs[0]['definition'].replace('\r\n', ' ')

    if len(out) > 400:
        out = out[:out.rfind(' ', 0, 400)] + '...'

    return out

# define plugin by GhettoWizard & Scaevolus


@hook.command('dict')
@hook.command
def define(inp):
    ".define/.dict <word> - fetches definition of <word>"

    url = 'http://ninjawords.com/'

    try:
        h = http.get_html(url + http.quote_plus(inp))
    except:
        return "API error; please try again in a few minutes."

    definition = h.xpath('//dd[@class="article"] | '
                         '//div[@class="definition"] |'
                         '//div[@class="example"]')

    if not definition:
        return 'No results for ' + inp

    def format_output(show_examples):
        result = '%s: ' % h.xpath('//dt[@class="title-word"]/a/text()')[0]

        correction = h.xpath('//span[@class="correct-word"]/text()')
        if correction:
            result = 'definition for "%s": ' % correction[0]

        sections = []
        for section in definition:
            if section.attrib['class'] == 'article':
                sections += [[section.text_content() + ': ']]
            elif section.attrib['class'] == 'example':
                if show_examples:
                    sections[-1][-1] += ' ' + section.text_content()
            else:
                sections[-1] += [section.text_content()]

        for article in sections:
            result += article[0]
            if len(article) > 2:
                result += ' '.join('%d. %s' % (n + 1, section)
                                   for n, section in enumerate(article[1:]))
            else:
                result += article[1] + ' '

        synonyms = h.xpath('//dd[@class="synonyms"]')
        if synonyms:
            result += synonyms[0].text_content()

        result = re.sub(r'\s+', ' ', result)
        result = re.sub('\xb0', '', result)
        return result

    result = format_output(True)
    if len(result) > 450:
        result = format_output(False)

    if len(result) > 450:
        result = result[:result.rfind(' ', 0, 450)]
        result = re.sub(r'[^A-Za-z]+\.?$', '', result) + ' ...'

    return result


@hook.command('e')
@hook.command
def etymology(inp):
    ".e/.etymology <word> - Retrieves the etymology of chosen word"

    url = 'http://www.etymonline.com/index.php'

    h = http.get_html(url, term=inp)

    etym = h.xpath('//dl')

    if not etym:
        return 'No etymology found for ' + inp

    etym = etym[0].text_content()

    etym = ' '.join(etym.split())

    if len(etym) > 400:
        etym = etym[:etym.rfind(' ', 0, 400)] + ' ...'

    return etym

'''Searches Encyclopedia Dramatica and returns the first paragraph of the
article'''


api_url = "http://encyclopediadramatica.es/api.php?action=opensearch"
ed_url = "http://encyclopediadramatica.es/"


@hook.command('ed')
@hook.command
def drama(inp):
    '''.drama <phrase> - gets first paragraph of Encyclopedia Dramatica article on <phrase>; Note, use proper calitalization e.g. "Ron Paul"'''
    try:
        j = http.get_json(api_url, search=inp)
    except:
        return "Error parsing Encyclopedia Dramatica API, please try again in a few minutes"
    if not j[1]:
        return 'no results found'
    article_name = j[1][0].replace(' ', '_').encode('utf8')

    url = ed_url + http.quote(article_name, '')
    page = http.get_html(url)

    for p in page.xpath('//div[@id="bodyContent"]/p'):
        if p.text_content():
            summary = ' '.join(p.text_content().splitlines())
            if len(summary) > 300:
                summary = summary[:summary.rfind(' ', 0, 300)] + "..."
            return '%s :: \x02%s\x02' % (summary, url)

    return "error"
