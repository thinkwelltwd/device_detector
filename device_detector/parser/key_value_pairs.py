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

    # iPhone/2025.26  iPhone14,5|26.0.1|390|844|3.00|AmericanAirlines
    # iPad/2025.30  iPad8,10|18.6.2|1194|834|2.00|AmericanAirlines
    RegexLazyIgnore(r'\|(?P<version>[\.\d]+).*\|(?P<name>AmericanAirlines)'),

    # Bloomberg|iOS|12.1.2|5.12.7|1d45e9c714c08ddcd8b8d51096f50ee7e2a28060
    # BloombergHorseshoe|iPadOS|15.5|5.77.1|a19956f55bf6a16b94ba5f239226c5ae77f2e3b5
    RegexLazyIgnore(r'(?P<name>[a-zA-Z]+)\|(?:ios|ipados)\|[\.\d]+\|(?P<version>[\d\.\-\w\&\?]+)\|'),

    # EmarsysPredictSDK|osversion:15.3|platform:ios
    RegexLazyIgnore(r'(?P<name>[a-zA-Z]+)\|[a-z\:]+(?P<version>[\d\.]+)'),
)

# Extra name / version from UAs
NAME_VERSION_REGEXES = (

    # Get <key>/<value> or <key> <value> pair from the beginning of the regex
    # generic ua string/1.23.2
    # Call & Chat/1 CFNetwork/902.2 Darwin/17.7.0
    # Microsoft SkyDriveSync 18.091.0506.0007 ship; Windows NT 10.0 (17134)
    # Ensure that User Agents like:
    # Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/Version/25.7.0 Hunt/1398
    # match "Hunt/1398" rather than "25.7.0 Hunt/1398"
    RegexLazyIgnore(r'^(?P<name>[\w\d\.\-_\'!®\?, \+\&]+)[ /](?P<version>[\d\.]+)'),

    # Extract "Opera Mobi/ADR-25672775" in User Agents like:
    # Opera/9.62 (Android 4.1.2; Linux; Opera Mobi/ADR-25672775) Presto/2.520.13 Version/12.520
    RegexLazyIgnore(r'\b(?P<name>[a-zA-Z\. \-_\'!®\?,\+\&]+)/(?P<version>[\d\.\w-]+)'),

    # Get ALL <key>/<value> pairs from the regex
    RegexLazyIgnore(r'(?P<name>[\w\d\.\-_\'!®\?,\+\&]+)/(?P<version>[\d\.\-\w\&\?]+)\b'),

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

    # Get <key><value> pair from beginning of regex, when name & version are not delimited
    # BlueApron2.47.0 (iPhone; iOS 12.1.3; Scale/2.0)
    RegexLazyIgnore(r'^(?P<name>[a-zA-Z\-_\'!®\?, \+\&]+)(?P<version>[\d\.]+)\b'),
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
