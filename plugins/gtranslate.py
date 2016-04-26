from util import hook, http

default_lang = 'en'
max_length = 100


def goog_trans(api_key, text, source, target):
    url = 'https://www.googleapis.com/language/translate/v2'

    if len(text) > max_length:
        return "This command only supports input of less then 100 characters."

    params = {
        'q': text,
        'key': api_key['access'],
        'target': target or default_lang,
        'format': 'text'
    }

    if source:
        params['source'] = source

    parsed = http.get_json(url, query_params=params)

    if parsed.get('error'):
        if parsed['error']['code'] == 403:
            return "The Translate API is off in the Google Developers Console."
        else:
            return "Google API error."

    if not target:
        return u'(%(detectedSourceLanguage)s) %(translatedText)s' % (parsed['data']['translations'][0])
    return u'%(translatedText)s' % parsed['data']['translations'][0]


def match_language(fragment):
    fragment = fragment.lower()
    for short, _ in lang_pairs:
        if fragment in short.lower().split():
            return short.split()[0]

    for short, full in lang_pairs:
        if fragment in full.lower():
            return short.split()[0]

    return None


@hook.api_key('google')
@hook.command
def translate(inp, api_key=None):
    ".translate [[source language] target language] <sentence> - " \
    "Translates <sentence> from source language (default autodetect) " \
    "to target language (default English) using Google Translate."
    if api_key.get('access', None) is None:
        return "Error: API keys not set."

    args = inp.split(' ', 2)
    try:
        if len(args) >= 2:
            tl = match_language(args[0])
            if not tl:
                return goog_trans(api_key, inp, '', '')
            if len(args) == 2:
                return goog_trans(api_key, args[1], '', tl)
            if len(args) >= 3:
                sl = match_language(args[1])
                if not sl:
                    return goog_trans(api_key, args[1] + ' ' + args[2], '', tl)
                return goog_trans(api_key, args[2], tl, sl)  # reversed on purpose
        return goog_trans(api_key, inp, '', '')
    except Exception as e:
        return e


lang_pairs = [
    ("af", "Afrikaans"),
    ("ar", "Arabic"),
    ("az", "Azerbaijani"),
    ("be", "Belarusian"),
    ("bg", "Bulgarian"),
    ("ca", "Catalan"),
    ("zh-CN zh cn", "Chinese"),
    ("cs", "Czech"),
    ("cy", "Welsh"),
    ("da", "Danish"),
    ("de", "German"),
    ("el", "Greek"),
    ("en", "English"),
    ("es sp", "Spanish"),
    ("et", "Estonian"),
    ("eu", "Basque"),
    ("fa", "Persian"),
    ("fi", "Finnish"),
    ("fr", "French"),
    ("ga", "Irish"),
    ("gl", "Galician"),
    ("hi", "Hindi"),
    ("hr", "Croatian"),
    ("ht", "Haitian Creole"),
    ("ht", "Haitian Creole"),
    ("hu", "Hungarian"),
    ("hy", "Armenian"),
    ("id", "Indonesian"),
    ("is", "Icelandic"),
    ("it", "Italian"),
    ("it", "Italian"),
    ("iw", "Hebrew"),
    ("ja jp jpn", "Japanese"),
    ("ka", "Georgian"),
    ("ko", "Korean"),
    ("lt", "Lithuanian"),
    ("lv", "Latvian"),
    ("mk", "Macedonian"),
    ("ms", "Malay"),
    ("mt", "Maltese"),
    ("nl", "Dutch"),
    ("no", "Norwegian"),
    ("no", "Norwegian"),
    ("pl", "Polish"),
    ("pt", "Portuguese"),
    ("ro", "Romanian"),
    ("ru", "Russian"),
    ("sk", "Slovak"),
    ("sl", "Slovenian"),
    ("sq", "Albanian"),
    ("sr", "Serbian"),
    ("sv", "Swedish"),
    ("sw", "Swahili"),
    ("th", "Thai"),
    ("tl", "Filipino"),
    ("tr", "Turkish"),
    ("uk", "Ukrainian"),
    ("ur", "Urdu"),
    ("vi", "Vietnamese"),
    ("yi", "Yiddish")
]
