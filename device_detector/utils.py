from hashlib import blake2s
from string import punctuation
try:
    import regex as re
except (ImportError, ModuleNotFoundError):
    import re
from urllib.parse import unquote

trans_tbl = str.maketrans({p: '' for p in punctuation})
punctuation_tbl = str.maketrans({p: '' for p in ' /.'})
REPEATED_CHARACTERS = re.compile(r'(.)(\1{11,})')


def ua_hash(user_agent):
    """
    Return short hash of User Agent string for
    memory-efficient cache key.
    """
    return blake2s(user_agent.encode('utf-8')).hexdigest()[:9]


def long_ua_no_punctuation(user_agent):
    """
    UserAgent string is long and has no Space, Dot or Slash
    """
    if len(user_agent) < 65:
        return False
    punc_removed = user_agent.translate(punctuation_tbl)
    return punc_removed == user_agent


def only_numerals_and_punctuation(user_agent):
    """
    Remove all punctuation. If only digits remain,
    don't bother saving, as nothing can be learned.

    21/4.35.1.2
    5.0.6
    """
    return user_agent.translate(trans_tbl).isdigit()


def mostly_numerals(user_agent):
    """
    UserAgent string is mostly numeric, discard
    15B93
    """
    alphabetic_chars = 0
    for char in user_agent:
        if not char.isnumeric():
            alphabetic_chars += 1

    return alphabetic_chars < 2


def clean_ua(user_agent):
    """
    Normalize and decode User Agent string
    """
    ua = unquote(user_agent)
    # sprd-Galaxy-S4/1.0 Linux/2.6.35.7 Android/4.2.2 Release/10.14.2013 Browser/AppleWebKit533.1 (KHTML, like Gecko) Mozilla/5.0 Mobile
    # sprd-lingwin-U820S/1.0 Linux/2.6.35.7 Android/2.3.5 Release/10.15.2012 Browser/AppleWebKit533.1 (KHTML, like Gecko) Mozilla/5.0 Mobile
    if ua.startswith('sprd-'):
        return ua[5:]

    return ua


def mostly_repeating_characters(user_agent):
    """
    User Agent string is mostly repeating characters
    """
    # Remove repeated characters like "baaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    # match 12+ repetitions to avoid UUIDs like "00000000-0000-0000-0000-000000000000"

    try:
        match = REPEATED_CHARACTERS.search(user_agent).group(2)
        return len(match) * 1.25 > len(user_agent)
    except (AttributeError, IndexError):
        return False


def version_from_key(name_version_pairs, default_version=None):
    """
    Some UA strings specify the app version in a separate Version/<float> pair.
    Mozilla/5.0 (iPhone; CPU iPhone OS 10_0 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) News/582.1 Version/2.0
    If so, return that version number.

    :param name_version_pairs:  [('news', 'News', '582.1'), ('version', 'Version', '2.0')]
    :param default_version: Default version if not found in name_version_pairs
    """

    for code, name, version in name_version_pairs:
        if code == 'version':
            return version

    return default_version


__all__ = (
    'ua_hash',
    'long_ua_no_punctuation',
    'only_numerals_and_punctuation',
    'mostly_numerals',
    'clean_ua',
    'mostly_repeating_characters',
    'version_from_key',
)
