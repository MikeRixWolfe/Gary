import re

from util import hook, http, text


@hook.api_key('wolframalpha')
@hook.command('calc')
@hook.command
def wa(inp, api_key=None):
    """.wa/.calc <query> - Computes <query> using Wolfram Alpha."""

    url = 'http://api.wolframalpha.com/v2/query?format=plaintext'

    try:
        result = http.get_xml(url, input=inp, appid=api_key)
    except:
        return "WolframAlpha query timed out for '%s'" % inp

    pod_texts = []
    for pod in result.xpath("//pod"):
        title = pod.attrib['title']
        if pod.attrib['id'] == 'Input':
            continue

        results = []
        for subpod in pod.xpath('subpod/plaintext/text()'):
            subpod = subpod.strip().replace('\\n', '; ')
            subpod = re.sub(r'\s+', ' ', subpod)
            if subpod:
                results.append(subpod)
        if results:
            pod_texts.append(title + ': ' + '|'.join(results))

    ret = '. '.join(pod_texts)

    if not pod_texts:
        return 'No results'

    ret = re.sub(r'\\(.)', r'\1', ret)

    def unicode_sub(match):
        return unichr(int(match.group(1), 16))

    ret = re.sub(r'\\:([0-9a-z]{4})', unicode_sub, ret)

    if not ret:
        return 'No results'

    return text.truncate_str(ret.split('. ')[0], 230)
