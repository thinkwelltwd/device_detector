try:
    import regex as re
except (ImportError, ModuleNotFoundError):
    import re

from .settings import SKIP_PREFIXES


CONTAINS_URL = re.compile(
    r'https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)',
    re.IGNORECASE,
)

REGEXES = (

    # Get ALL <key>/<value> pairs from the regex
    re.compile(
        r'(?P<name>[\w\d\.\-_\&\'!®\?, \+\&]+)/(?P<version>[\d\.\-\w\&\?]+)\b',
        re.IGNORECASE,
    ),

    # <name><space><version> - anchored at the beginning
    # CarboniteDownloader 6.3.2 build 7466 (Sep-07-2017)
    # libreoffice 5.4.3.2 (92a7159f7e4af62137622921e809f8546db437e5; windows; x86;)
    # openoffice.org 3.2 (320m18(build:9502); windows; x86; bundledlanguages=en-us)
    re.compile(
        r'^(?P<name>[\w\._\&\'!®\?,\+\&]+) [rv]?(?P<version>[\d\.\-\&\?]+)\b',
        re.IGNORECASE,
    ),

    # <name><sep><version> - anywhere in string
    # Microsoft Office Access 2013 (15.0.4693) Windows NT 6.2, where version == 15.0.4693
    # Microsoft.VisualStudio.Help (2.3)
    # Microsoft URL Control - 6.01.9782
    # openshot-qt-2.4.2
    # DigiCal (v1.8.2b; http://digibites.nl/digical)
    # iPad; 10.3.3; autotrader.com; 3.0.10
    re.compile(
        r'(?P<name>[\w\d\.\-_\&\'!®\?, \+]+) ?[(\-;] ?[vr]?(?P<version>[\d\.]+)(?:\b|\w|$)',
        re.IGNORECASE,
    ),

    # <name><space><version> - anywhere in remainder of string
    # Mozilla/5.0 AppleWebKit/537.36 Mobile Safari/537.36 Android SermonAudio.com 1.9.8, wanting "SermonAudio.com 1.9.8"
    re.compile(
        r'(?P<name>[\w\._\&\'!®\?,\+\& ]+) [rv]?(?P<version>[\d\.\-\&\?]+)\b',
        re.IGNORECASE,
    ),

)

# <name>/<version> pairs with names matching these
# regexes are not considered interesting
SKIP_NAME_REGEXES = [
    # Android; samsung-SAMSUNG-SM-T377A; 6.0.1; AutoTrader.com; 2.6.4.3.236
    re.compile(r'samsung[- ]sm', re.IGNORECASE),

    # Mozilla/5.0 (iPhone; iPhone103; 12.1.4) MLN/4.30.450041483 (0f3d913a35528d98b8793f4d7aa0539e)"
    re.compile(r'^(iphone|ipad)\d', re.IGNORECASE),
]


def name_matches_regex(name) -> bool:
    """
    If name matches regex, then don't
    want its name/version pair.
    """
    for rgx in SKIP_NAME_REGEXES:
        if rgx.search(name) is not None:
            return True

    return False


def extract_pairs(regex, ua):
    """
    Extract all key/value pairs of the specified regex,
    and return pairs along with unmatched portion of ua string.
    """
    matches = regex.findall(ua)
    substring = ua

    if matches:
        substring = regex.sub(' ', ua)

    pairs = []
    for name, version in matches:
        name = name.strip(' -,')
        if not name:
            continue

        name_lower = name.lower()
        if name_lower in SKIP_PREFIXES:
            continue

        if name_matches_regex(name):
            continue

        code = name_lower.replace(' ', '')
        pairs.append((code, name, version.strip()))

    return pairs, substring


def key_value_pairs(ua):
    """
    Extract key/value pairs from User Agent String
    """

    substring = CONTAINS_URL.sub(' ', ua)

    all_pairs = []

    for rgx in REGEXES:
        pairs, substring = extract_pairs(rgx, substring)
        all_pairs.extend(pairs)

    return all_pairs


__all__ = (
    'extract_pairs',
    'key_value_pairs',
)
