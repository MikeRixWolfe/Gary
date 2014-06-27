from util import hook, text, web
import hashlib

# basic text tools

# TODO: make this capitalize sentences correctly


@hook.command("capitalise")
@hook.command
def capitalize(inp):
#    """capitalize <string> - Capitalizes <string>."""
    return inp.capitalize()


@hook.command
def upper(inp):
#    """upper <string> - Convert string to uppercase."""
    return inp.upper()


@hook.command
def lower(inp):
#    """lower <string> - Convert string to lowercase."""
    return inp.lower()


@hook.command
def titlecase(inp):
#    """title <string> - Convert string to title case."""
    return inp.title()


@hook.command
def swapcase(inp):
#    """swapcase <string> - Swaps the capitalization of <string>."""
    return inp.swapcase()


@hook.command
def reverse(inp):
#    """Enter a string and the bot will reverse it and print it out."""
    return "%s" % (inp[::-1],)

# encoding


@hook.command
def rot13(inp):
    """rot13 <string> - Encode <string> with rot13."""
    return inp.encode('rot13')


@hook.command
def base64(inp):
#    """base64 <string> - Encode <string> with base64."""
    return inp.encode('base64')


@hook.command
def unbase64(inp):
#    """unbase64 <string> - Decode <string> with base64."""
    return inp.decode('base64')


@hook.command
def checkbase64(inp):
    try:
        decoded = inp.decode('base64')
        recoded = decoded.encode('base64').strip()
        is_base64 = recoded == inp
    except:
        is_base64 = False

    if is_base64:
        return '"{}" is base64 encoded'.format(recoded)
    else:
        return '"{}" is not base64 encoded'.format(inp)


@hook.command
def unescape(inp):
#    """unescape <string> - Unescapes <string>."""
    try:
        return inp.decode('unicode-escape')
    except Exception as e:
        return "Error: {}".format(e)


@hook.command
def escape(inp):
#    """escape <string> - Escapes <string>."""
    try:
        return inp.encode('unicode-escape')
    except Exception as e:
        return "Error: {}".format(e)

# length


@hook.command
def length(inp):
#    """length <string> - gets the length of <string>"""
    return "The length of that string is {} characters.".format(len(inp))

# hashing


@hook.command
def md5(inp):
#    "md5 <string> - Encode <string> with md5."
    return hashlib.md5(inp).hexdigest()


@hook.command
def sha1(inp):
#    "sha1 <string> - Encode <string> with sha1."
    return hashlib.sha1(inp).hexdigest()


@hook.command
def sha256(inp):
#    "sha256 <string> - Encode <string> with sha256."
    return hashlib.sha256(inp).hexdigest()


@hook.command
def hash(inp):
    """hash <string> - Returns hashes of <string>."""
    return ', '.join(x + ": " + getattr(hashlib, x)(inp).hexdigest()
                     for x in ['md5', 'sha1', 'sha256'])

# novelty


@hook.command
def munge(inp):
#    """munge <text> - Munges up <text>."""
    return text.munge(inp)

# colors - based on code by Reece Selwood - <https://github.com/hitzler/homero>

@hook.command(autohelp=False)
def spam(inp, say=None):
    say(text.rainbow("~SPAM~"))


@hook.command
def shorten(inp):
    #".shorten <url> - Shortens a URL with goo.gl"
    url = web.try_googl(inp)
    return url
