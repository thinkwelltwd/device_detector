from hashlib import blake2s
from string import punctuation
from urllib.parse import unquote
from .lazy_regex import RegexLazy, RegexLazyIgnore

trans_tbl = str.maketrans({p: '' for p in punctuation})
punctuation_tbl = str.maketrans({p: '' for p in ' /.'})
REPEATED_CHARACTERS = RegexLazy(r'(.)(\1{11,})')

# Safari often appends a meaningless alphanumeric string enclosed in parens.
# Otherwise the UAs are identical so strip that suffix
# Mozilla/5.0 (iPhone; CPU iPhone OS 12_1_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/16C101 (5836419392)
# Mozilla/5.0 (iPhone; CPU iPhone OS 12_1_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/16D57 baidumap_IPHO (10793838272)
STRIP_NUM_SUFFIX = RegexLazyIgnore(r'(\([0-9]+\))$')


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
    ua = unquote(STRIP_NUM_SUFFIX.sub('', user_agent)).strip()
    ua_lower = ua.lower()

    for prefix in (
            # sprd-Galaxy-S4/1.0 Linux/2.6.35.7 Android/4.2.2 Release/10.14.2013 Browser/AppleWebKit533.1 (KHTML, like Gecko) Mozilla/5.0 Mobile
            # sprd-lingwin-U820S/1.0 Linux/2.6.35.7 Android/2.3.5 Release/10.15.2012 Browser/AppleWebKit533.1 (KHTML, like Gecko) Mozilla/5.0 Mobile
            'sprd-',

            # null (FlipboardProxy/1.1; http://flipboard.com/browserproxy)
            # (null) MyOperations/3.0.0/162 JDM/1.0
            'null',
            '(null)',

            # AmazonWebView/Kindle for iOS/6.9.1.3/iOS/11.4.1/iPhone
            # AmazonWebView/PrimeNow/5.7/iOS/11.4.1/iPhone
            # AmazonWebView/Prime Video/5.71.1526.2/iOS/11.4.1/iPad
            # AmazonWebView/SellingServicesOnAmazon/1.1.7/iPhone OS/11.3.1/iPhone
            'amazonwebview',
    ):
        if ua_lower.startswith(prefix):
            return ua[len(prefix):].strip()

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


def calculate_dtype(app_name) -> str:
    """
    For generic extractors try to return a more
    specific type we can be if reasonably sure.
    """
    app_name_lower = app_name.lower()
    for name, dtype in (
        ('update', 'desktop app'),
        ('mail', 'pim'),
        ('api', 'library'),
        ('sdk', 'library'),
        ('webview', 'browser'),
    ):
        if name in app_name_lower:
            return dtype

    return 'generic'


__all__ = (
    'calculate_dtype',
    'ua_hash',
    'long_ua_no_punctuation',
    'only_numerals_and_punctuation',
    'mostly_numerals',
    'clean_ua',
    'mostly_repeating_characters',
)
