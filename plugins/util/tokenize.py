from re import sub


def tokenize(text):
    tokens = { '@': [], '+': [], '-': [], '=': [] }
    active_token = None
    active_token_type = None

    text = sub(r'([\@\+\=\-]) +', r'\1', text)
    text = sub(r'(.* +\@\S+|^\@\S+) +((?![\@\+\-\=]).+)', r'\1 +\2', text)
    text = [t for t in text.split(' ') if t]

    for word in text:
        if active_token and active_token_type:
            if word[0] in tokens.keys():
                tokens[active_token_type].append(' '.join(active_token))
                active_token_type, active_token = word[0], [word[1:]]
            else:
                active_token.append(word)
        else:
            if word[0] in tokens.keys():
                active_token_type, active_token = word[0], [word[1:]]
            else:
                active_token_type, active_token = '+', [word]

    tokens[active_token_type].append(' '.join(active_token))

    return tokens


def format(tokens):
    nick = next(iter(['nick:"{}"'.format(t) for t in tokens['@']]), None)

    include = ' AND '.join(['msg:"{}"*'.format(t) for t in tokens['+']])
    exact = ' AND '.join(['msg:"{}"'.format(t) for t in tokens['=']])
    include = ' AND '.join([t for t in [include, exact] if t])

    exclude = ' NOT '.join(['msg:"{}"'.format(t) for t in tokens['-']])
    exclude = 'NOT ' + exclude if exclude else exclude

    msgs = [m for m in [include, exclude] if m]

    if nick:
        if msgs:
            return "{} AND ({})".format(nick, ' '.join(msgs))
        else:
            return nick
    else:
        return "({})".format(' '.join(msgs))


def build_query(text):
    return format(tokenize(text))

