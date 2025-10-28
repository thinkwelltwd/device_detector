import regex
from ..lazy_regex import RegexLazyIgnore
from .settings import SKIP_PREFIXES

CONTAINS_URL = RegexLazyIgnore(
    r'https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)',
)

# fmt: off
# Extra version / name from UAs
VERSION_NAME_REGEXES = (
    # 1.172.0.1 - LIVE - Mar 5 2020
    # 17build 113411 LIVE Sep 17 20180
    RegexLazyIgnore(r'(?P<version>[\d\.]+)[ \-]+(?P<name>LIVE)'),

    # 15.5.53 Boxcar
    # 165 CandyCanes
    RegexLazyIgnore(r'^(?P<version>[\d\.]+)[ \-/]+(?P<name>\w+)$'),
)

# Extra name / version from UAs
NAME_VERSION_REGEXES = (

    # Get ALL <key>/<value> pairs from the regex
    RegexLazyIgnore(r'(?P<name>[\w\d\.\-_\&\'!®\?, \+\&]+)/(?P<version>[\d\.\-\w\&\?]+)\b'),

    # <name><space><version> - anchored at the beginning
    # CarboniteDownloader 6.3.2 build 7466 (Sep-07-2017)
    # libreoffice 5.4.3.2 (92a7159f7e4af62137622921e809f8546db437e5; windows; x86;)
    # openoffice.org 3.2 (320m18(build:9502); windows; x86; bundledlanguages=en-us)
    RegexLazyIgnore(r'^(?P<name>[\w\._\&\'!®\?,\+\&]+) [rv]?(?P<version>[\d\.\-\&\?]+)\b'),

    # <name><sep><version> - anywhere in string
    # Microsoft Office Access 2013 (15.0.4693) Windows NT 6.2, where version == 15.0.4693
    # Microsoft.VisualStudio.Help (2.3)
    # Microsoft URL Control - 6.01.9782
    # openshot-qt-2.4.2
    # DigiCal (v1.8.2b; http://digibites.nl/digical)
    # iPad; 10.3.3; autotrader.com; 3.0.10
    RegexLazyIgnore(
        r'(?P<name>[\w\d\.\-_\&\'!®\?, \+]+) ?[(\-;] ?[vr]?(?P<version>[\d\.]+)(?:\b|\w|$)'
    ),

    # <name><space><version> - anywhere in remainder of string
    # Mozilla/5.0 AppleWebKit/537.36 Mobile Safari/537.36 Android SermonAudio.com 1.9.8, wanting "SermonAudio.com 1.9.8"
    RegexLazyIgnore(r'(?P<name>[\w\._\&\'!®\?,\+\& ]+) [rv]?(?P<version>[\d\.\-\&\?]+)\b'),
)

# <name>/<version> pairs with names matching these
# regexes are not considered interesting
SKIP_NAME_REGEXES = [
    # Android; samsung-SAMSUNG-SM-T377A; 6.0.1; AutoTrader.com; 2.6.4.3.236
    RegexLazyIgnore(r'samsung[- ]sm'),

    # Mozilla/5.0 (iPhone; iPhone103; 12.1.4) MLN/4.30.450041483 (0f3d913a35528d98b8793f4d7aa0539e)"
    RegexLazyIgnore(r'^(iphone|ipad)\d'),
]
# fmt: on


def name_matches_regex(name: str) -> bool:
    """
    If name matches regex, then don't
    want its name/version pair.
    """
    for rgx in SKIP_NAME_REGEXES:
        if rgx.search(name) is not None:
            return True

    return False


def scrub_name_version_pairs(matches: list[tuple[str, str]]) -> list:
    """
    Takes list of (name,version) tuples.
    Remove all pairs where name matches SKIP patterns
    """
    pairs = []
    for name, version in matches:
        name = name.strip(' -,')
        if not name:
            continue

        # does this look like base64 encoded data?
        if name.endswith('=='):
            continue

        name_lower = name.lower()
        if name_lower in SKIP_PREFIXES:
            continue

        if name_matches_regex(name):
            continue

        code = name_lower.replace(' ', '')
        pairs.append((code, name, version.strip()))

    return pairs


def extract_version_name_pairs(rgx: regex.Pattern, ua: str) -> list[tuple[str, str]]:
    """
    Extract all key/value pairs of the specified regex,
    where key==version and value==name
    and return pairs along with unmatched portion of ua string.
    """
    if matched := rgx.search(ua):
        return scrub_name_version_pairs([(matched.group('name'), matched.group('version'))])

    return []


def extract_name_version_pairs(rgx: regex.Pattern, ua: str) -> tuple:
    """
    Extract all key/value pairs of the specified regex,
    where key==name and value==version
    and return pairs along with unmatched portion of ua string.
    """
    substring = ua

    if matches := rgx.findall(ua):
        substring = rgx.sub(' ', ua)

    pairs = scrub_name_version_pairs(matches)

    return pairs, substring


def key_value_pairs(ua: str) -> list[tuple[str, str]]:
    """
    Extract key/value pairs from User Agent String
    """

    substring = CONTAINS_URL.sub(' ', ua)

    all_pairs = []

    for rgx in VERSION_NAME_REGEXES:
        pairs = extract_version_name_pairs(rgx, substring)
        if pairs:
            all_pairs.extend(pairs)

    # <version>/<name> regexes will be much less common
    # so if we found such entries return then first
    if all_pairs:
        return all_pairs

    for rgx in NAME_VERSION_REGEXES:
        pairs, substring = extract_name_version_pairs(rgx, substring)
        all_pairs.extend(pairs)

    return all_pairs


__all__ = (
    'extract_name_version_pairs',
    'key_value_pairs',
)
