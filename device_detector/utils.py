from collections import Counter
from hashlib import blake2s
from string import punctuation
from urllib.parse import unquote
from .enums import AppType
from .lazy_regex import RegexLazy, RegexLazyIgnore

PUNC_SPACE = f'{punctuation} '
trans_tbl = str.maketrans(dict.fromkeys(PUNC_SPACE, ''))
punctuation_tbl = str.maketrans(dict.fromkeys(' /.', ''))
number_table = str.maketrans(dict.fromkeys('0123456789', ''))
REPEATED_CHARACTERS = RegexLazy(r'(.)(\1{11,})')

# Safari often appends a meaningless alphanumeric string enclosed in parens.
# Otherwise, the UAs are identical so strip that suffix
# Mozilla/5.0 (iPhone; CPU iPhone OS 12_1_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/16C101 (5836419392)  # noqa
# Mozilla/5.0 (iPhone; CPU iPhone OS 12_1_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/16D57 baidumap_IPHO (10793838272)  # noqa
STRIP_NUM_SUFFIX = RegexLazyIgnore(r'(\([0-9]+\))$')
COMMON_BIGRAMS = RegexLazyIgnore(
    r'th|he|in|er|an|ar|re|on|at|en|nd|ti|es|or|te|of|ed|is|it|al|ar|st|to|nt|ng|se|'
    r'ha|as|ou|io|le|ve|co|me|de|hi|ri|ro|ic|ne|ea|ee|oo|ra|ce|li|ch|ll|be|ma|si|om|ur'
)
ILLEGAL_BIGRAMS = RegexLazyIgnore(r'[a-z0-9](jq|qg|qk|qy|qz|wq|wz)')
LEGAL_BIGRAMS = RegexLazyIgnore(
    '(aa|ba|ca|da|ea|fa|ga|ha|ia|ja|ka|la|ma|na|oa|pa|qa|ra|sa|ta|ua|va|wa|xa|ya|za|ab|bb|cb|db|eb'
    '|fb|gb|hb|ib|jb|kb|lb|mb|nb|ob|pb|qb|rb|sb|tb|ub|vb|wb|xb|yb|zb|ac|bc|cc|dc|ec|fc|gc|hc|ic|jc'
    '|kc|lc|mc|nc|oc|pc|qc|rc|sc|tc|uc|vc|wc|xc|yc|zc|ad|bd|cd|dd|ed|fd|gd|hd|id|jd|kd|ld|md|nd|od'
    '|pd|qd|rd|sd|td|ud|vd|wd|xd|yd|zd|ae|be|ce|de|ee|fe|ge|he|ie|je|ke|le|me|ne|oe|pe|qe|re|se|te'
    '|ue|ve|we|xe|ye|ze|af|bf|cf|df|ef|ff|gf|hf|if|jf|kf|lf|mf|nf|of|pf|qf|rf|sf|tf|uf|vf|wf|xf|yf'
    '|zf|ag|bg|cg|dg|eg|fg|gg|hg|ig|jg|kg|lg|mg|ng|og|pg|rg|sg|tg|ug|vg|wg|xg|yg|zg|ah|bh|ch|dh|eh'
    '|fh|gh|hh|ih|jh|kh|lh|mh|nh|oh|ph|qh|rh|sh|th|uh|vh|wh|xh|yh|zh|ai|bi|ci|di|ei|fi|gi|hi|ii|ji'
    '|ki|li|mi|ni|oi|pi|qi|ri|si|ti|ui|vi|wi|xi|yi|zi|aj|bj|cj|dj|ej|fj|gj|hj|ij|jj|kj|lj|mj|nj|oj'
    '|pj|qj|rj|sj|tj|uj|vj|wj|xj|yj|zj|ak|bk|ck|dk|ek|fk|gk|hk|ik|jk|kk|lk|mk|nk|ok|pk|rk|sk|tk|uk'
    '|vk|wk|xk|yk|zk|al|bl|cl|dl|el|fl|gl|hl|il|jl|kl|ll|ml|nl|ol|pl|ql|rl|sl|tl|ul|vl|wl|xl|yl|zl'
    '|am|bm|cm|dm|em|fm|gm|hm|im|jm|km|lm|mm|nm|om|pm|qm|rm|sm|tm|um|vm|wm|xm|ym|zm|an|bn|cn|dn|en'
    '|fn|gn|hn|in|jn|kn|ln|mn|nn|on|pn|qn|rn|sn|tn|un|vn|wn|xn|yn|zn|ao|bo|co|do|eo|fo|go|ho|io|jo'
    '|ko|lo|mo|no|oo|po|qo|ro|so|to|uo|vo|wo|xo|yo|zo|ap|bp|cp|dp|ep|fp|gp|hp|ip|jp|kp|lp|mp|np|op'
    '|pp|qp|rp|sp|tp|up|vp|wp|xp|yp|zp|aq|bq|cq|dq|eq|fq|gq|hq|iq|kq|lq|mq|nq|oq|pq|qq|rq|sq|tq|uq'
    '|vq|xq|yq|zq|ar|br|cr|dr|er|fr|gr|hr|ir|jr|kr|lr|mr|nr|or|pr|qr|rr|sr|tr|ur|vr|wr|xr|yr|zr|as'
    '|bs|cs|ds|es|fs|gs|hs|is|js|ks|ls|ms|ns|os|ps|qs|rs|ss|ts|us|vs|ws|xs|ys|zs|at|bt|ct|dt|et|ft'
    '|gt|ht|it|jt|kt|lt|mt|nt|ot|pt|qt|rt|st|tt|ut|vt|wt|xt|yt|zt|au|bu|cu|du|eu|fu|gu|hu|iu|ju|ku'
    '|lu|mu|nu|ou|pu|qu|ru|su|tu|uu|vu|wu|xu|yu|zu|av|bv|cv|dv|ev|fv|gv|hv|iv|jv|kv|lv|mv|nv|ov|pv'
    '|qv|rv|sv|tv|uv|vv|wv|xv|yv|zv|aw|bw|cw|dw|ew|fw|gw|hw|iw|jw|kw|lw|mw|nw|ow|pw|qw|rw|sw|tw|uw'
    '|vw|ww|xw|yw|zw|ax|bx|cx|dx|ex|fx|gx|hx|ix|jx|kx|lx|mx|nx|ox|px|qx|rx|sx|tx|ux|vx|wx|xx|yx|zx'
    '|ay|by|cy|dy|ey|fy|gy|hy|iy|jy|ky|ly|my|ny|oy|py|ry|sy|ty|uy|vy|wy|xy|yy|zy|az|bz|cz|dz|ez|fz'
    '|gz|hz|iz|jz|kz|lz|mz|nz|oz|pz|rz|sz|tz|uz|vz|wz|xz|yz|zz|3d|2p)'
)
COMMON_TRIGRAMS = RegexLazyIgnore(
    r'(the|and|ing|her|hat|his|tha|ere|for|lab|ent|ion|ter|was|you|ith|ver|all|wit|thi|tio|p2p|dev|'
    r'ink|jet|ios|mac|win|dos|rss|med|fun|sun|fax|app|api|bot|cam|cpu|lab|hue|rgb|sdk|web|oku|pad|'
    r'art|bea|boa|cat|law|mes|new|not|vpn|zig|4x4|gun|sim|mp3|wma|mov|pic|pix|vid|war|key|sho|syn|'
    r'bit|boy|cli|dri|han|log|man|mot|rad|oil|sip|nom|gen|per|sig|tim|tun|wor)'
)
COMMON_QUADRIGRAMS = RegexLazyIgnore(
    '(clou|ipod|ipad|that|ther|with|tion|here|ould|ight|have|hich|whic|this|thin|they|atio|ever|'
    'from|ough|were|hing|ment|droid|mobil|brows|load|micro|msdw|network|cloud|http|phone|tablet|'
    'wifi|window|page|cart|wiki|mozilla|chrome|vivaldi|view|traf|rack|game|audio|truck|block|moat|'
    'book|sport|widget|scan|connect|free|talk|school|tube|plus|tool|sheet|shop|kids|sing|date|play|'
    'client|girl|plan|proj|soft|tock|instal|linu|data|trav|stud|send|sale|phot|shar|wire|star|mail|'
    'win3|win6)'
)

UUID_LIKE_NAME = RegexLazyIgnore(
    "^([0-9a-f]{8}(-[0-9a-f]{4}){2,}$)|"
    "^([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$)"
)
# a_05D42541-648B-41DD-B11F-0CAF61F4CE19-660-0000004D54BA56F2
# a_03E848FE-2BD9-4400-B87B-172C35D4A309-3121-00000B5202325FA0
LONG_UUID = RegexLazyIgnore(r"^([\w\d]{10}-)+([\w\d]{4,5}-)+([\w\d]{12}-)([\w\d]{3,5}-)")
SHORT_UUID = RegexLazyIgnore(r"^(\w{4,8}-)(\w{4,8}-)+(\w{4,12})$")
TWO_SEGMENT_UUID = RegexLazyIgnore(r"^(\w{4,8}-)(\w{4,8})$")
INTEGER = RegexLazyIgnore(r"\d")
MIN_WORD_LENGTH = 7


def ua_hash(user_agent: str, headers: dict | None = None) -> str:
    """
    Return short hash of User Agent string for
    memory-efficient cache key.
    """
    if headers:
        try:
            cache_key = f'{user_agent}{"-".join(sorted(headers.values()))}'
        except TypeError:
            cache_key = f'{user_agent}{headers}'
    else:
        cache_key = user_agent

    return blake2s(cache_key.encode('utf-8')).hexdigest()


def long_ua_no_punctuation(user_agent: str) -> bool:
    """
    UserAgent string is long and has no Space, Dot or Slash
    """
    if len(user_agent) < 65:
        return False
    punc_removed = user_agent.translate(punctuation_tbl)
    return punc_removed == user_agent


def only_numerals_and_punctuation(user_agent: str) -> bool:
    """
    Remove all punctuation. If only digits remain,
    don't bother saving, as nothing can be learned.

    21/4.35.1.2
    5.0.6
    """
    return user_agent.translate(trans_tbl).isdigit()


def mostly_numerals(user_agent: str) -> bool:
    """
    UserAgent string is mostly numeric, discard
    15B93
    """
    if not user_agent or ' ' in user_agent:
        return False

    try:
        int(user_agent)
        return True
    except ValueError:
        pass

    alphabetic_chars = 0
    for char in user_agent:
        if not char.isnumeric():
            alphabetic_chars += 1

    return alphabetic_chars / len(user_agent) < 0.33


def clean_ua(user_agent: str, user_agent_lower: str) -> str:
    """
    Normalize and decode User Agent string
    """
    ua = unquote(STRIP_NUM_SUFFIX.sub('', user_agent)).strip()

    for prefix in (
        # sprd-Galaxy-S4/1.0 Linux/2.6.35.7 Android/4.2.2 Release/10.14.2013 Browser/AppleWebKit533.1 (KHTML, like Gecko) Mozilla/5.0 Mobile  # noqa
        # sprd-lingwin-U820S/1.0 Linux/2.6.35.7 Android/2.3.5 Release/10.15.2012 Browser/AppleWebKit533.1 (KHTML, like Gecko) Mozilla/5.0 Mobile  # noqa
        'sprd-',
        # null (FlipboardProxy/1.1; http://flipboard.com/browserproxy)
        # (null) MyOperations/3.0.0/162 JDM/1.0
        # (null)/14898/app_MUd3n2yw07Lg5hy0f8hRXuj1jI5ml17ww3haFrbKUBw/ios/2.4.0/iOS/12.1.4/gzip/s
        'null',
        '(null)',
        # AmazonWebView/Kindle for iOS/6.9.1.3/iOS/11.4.1/iPhone
        # AmazonWebView/PrimeNow/5.7/iOS/11.4.1/iPhone
        # AmazonWebView/Prime Video/5.71.1526.2/iOS/11.4.1/iPad
        # AmazonWebView/SellingServicesOnAmazon/1.1.7/iPhone OS/11.3.1/iPhone
        'amazonwebview',
        # com.usebutton.merchant/0.1.0-beta3 1 (iOS 11.4; iPhone8,4; com.tophatter.tophatter/4.33 614; Scale/2.00; en-US)
        # com.usebutton.merchant/1.0.0 1 (Android 6.0.1; samsung SM-G900V; com.walmart.grocery/7.1.0 7010103; Scale/3.0; en_us)
        # com.usebutton.merchant/1.0.0 1 (iOS 13.2.3; iPhone12,1; com.giddyinc.boxed.prod.00/2.9.4 2.9.4.11504; Scale/2.00; en-US)
        # com.usebutton.merchant/1.0.0 1 (iOS 13.2.3; iPhone12,1; com.houzz.app/19.12.15 4305; Scale/2.00; en-US)
        # com.usebutton.mparticle/7.9.2-1.0.0 (iOS 13.3; iPhone8,1; com.walmart.grocery/2001081028; Scale/2.0; en-US)
        # com.usebutton.mparticle/7.9.2-1.0.0 (iOS 13.3; iPhone9,1; com.walmart.electronics/2003032106; Scale/2.0; en-US)
        # com.usebutton.sdk/5.32.0 (iOS 12.2; iPhone10,1; com.hotwire.Hotwire/1732244; Scale/2.00; en-US; Build/appstore)
        # com.usebutton.sdk/5.32.0 (iOS 12.2; iPhone10,3; doordash.DoorDashConsumer/1; Scale/3.00; en-US; Build/appstore)
        'com.usebutton.',
        # FirebaseAuth.iOS/10.14.0 com.samsclub.samsapp/25.10.40 iPhone/26.0.1 hw/iPhone18_3 iOS 10.14.0 - Sam's Club - iPhone 17
        # FirebaseAuth.iOS/7.7.0 com.storytree.businessprints/4.7.9 iPhone/17.5.1 hw/iPhone12_1
        # FirebaseAuth.iOS/8.4.0 depollsoft.pitchperfect/2.0.3 iPhone/18.4 hw/iPhone14_6
        # FirebaseAuth.iOS/9.3.0 com.2mc.bidftamobile/4.26 iPhone/18.6 hw/iPhone12_8
        'firebaseauth.ios',
    ):
        if user_agent_lower.startswith(prefix):
            ua = ua[len(prefix) :].strip().strip('/')

    return ua


def mostly_repeating_characters(user_agent: str) -> bool:
    """
    User Agent string is mostly repeating characters
      - baaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
      - 00000000-0000-0000-0000-000000000000
    """
    if not user_agent or len(user_agent) > 100:
        return False

    counts = Counter(user_agent)
    return len(counts) / len(user_agent) < 0.15


def random_alphanumeric_string(user_agent: str) -> bool:
    """
    User Agent string is mostly generated names like:

    001471FmBjtgZvahkMJdcGJhhjXuuD99
    002261f23pRwrjIEtS1MrX0lZ4hx8N7P
    002353ueFfucaEDjKRbKwlpDpecxwYwC
    ziNICEarE9VlaPSkhDAyZrkZSpuEkIA
    vVNYZaiXO9Hd5zAi
    """
    if not user_agent or not user_agent.isascii() or good_ngram_matches(user_agent):
        return False

    # holav1_10593F39DD2DAEBC
    # HKUM_XBw3S
    # HKUM_fXHH8t9R
    if user_agent.startswith(('holav1_', 'hkum_')):
        return True

    # strings with adequate spaces / punctuation are not handled
    if (ua_length := len(user_agent)) <= MIN_WORD_LENGTH:
        return False

    if well_punctuated(user_agent, ua_length):
        return False

    vowels = 'aeiou'
    previous_is_int = user_agent[0].isnumeric()

    intermingled_integers = 1 if previous_is_int else 0

    longest_consonant_sequence = 0
    longest_vowel_sequence = 0

    current_consonant_sequence = 0
    current_vowel_sequence = 0

    for char in user_agent:
        char_is_numerical = char.isnumeric()

        if char_is_numerical:
            if not previous_is_int:
                intermingled_integers += 1
            reset_vowels = reset_consonants = previous_is_int = True

        elif char in vowels:
            current_vowel_sequence += 1
            reset_vowels, reset_consonants = False, True

        else:
            current_consonant_sequence += 1
            reset_vowels, reset_consonants = True, False

        if reset_vowels:
            current_vowel_sequence, longest_vowel_sequence = reset_sequences(
                current_vowel_sequence,
                longest_vowel_sequence,
            )

        if reset_consonants:
            current_consonant_sequence, longest_consonant_sequence = reset_sequences(
                current_consonant_sequence,
                longest_consonant_sequence,
            )

        if not char_is_numerical and previous_is_int:
            previous_is_int = False

    # update longest sequences after all chars are seen
    current_consonant_sequence, longest_consonant_sequence = reset_sequences(
        current_consonant_sequence,
        longest_consonant_sequence,
    )
    current_vowel_sequence, longest_vowel_sequence = reset_sequences(
        current_vowel_sequence,
        longest_vowel_sequence,
    )

    short_ua_len = 17
    alphabetic_threshold = 4 if ua_length < short_ua_len else 5
    intermingled_integer_threshold = 2 if ua_length < short_ua_len else 3

    gibberish = (
        longest_consonant_sequence >= alphabetic_threshold
        or longest_vowel_sequence >= alphabetic_threshold
        or intermingled_integers >= intermingled_integer_threshold
    )

    if gibberish and ua_length < short_ua_len:
        return ngram_analysis_gibberish(user_agent)

    return gibberish or ngram_analysis_gibberish(user_agent)


def well_punctuated(user_agent: str, ua_length: int) -> bool:
    """
    User Agents should have a number of spaces & punctuation characters.
    UAs with adequate spaces / punctuation are not gibberish.
    """
    punctuation_removed_diff = ua_length - len(user_agent.translate(trans_tbl))
    if ua_length <= 20:
        delta = 1
    elif ua_length <= 35:
        delta = 2
    else:
        delta = 3

    return punctuation_removed_diff >= delta


def ngram_analysis_gibberish(user_agent: str) -> bool:
    """
    Analyze legal ngrams to see if it's likely that UA is gibberish.
    """
    ua_length = len(user_agent)

    if ua_length <= 6:
        bigram_threshold = 3
    elif ua_length <= 10:
        bigram_threshold = 4
    elif ua_length <= 15:
        bigram_threshold = 5
    elif ua_length <= 20:
        bigram_threshold = 7
    elif ua_length <= 30:
        bigram_threshold = 10
    else:
        bigram_threshold = 15

    legal_bigram_matches = LEGAL_BIGRAMS.findall(user_agent)
    unique_bigrams = len(legal_bigram_matches)

    return bigram_threshold > unique_bigrams


def good_ngram_matches(user_agent: str) -> bool:
    """
    User agent likely NOT gibberish due to containing
    quadrigrams or trigrams.

    Quadrigrams:
       - Wordswithfriends3
       - ZooskAndroid

    Trigrams:
       - ZipsCarWash
       - JQSmartBand
    """
    if COMMON_QUADRIGRAMS.search(user_agent):
        return True

    trigram_match = COMMON_TRIGRAMS.findall(user_agent)
    ua_length = len(user_agent)

    if ua_length < 24 and trigram_match or len(trigram_match) >= 2:
        return True

    if ua_length <= 12:
        bigram_threshold = 2
    elif ua_length <= 24:
        bigram_threshold = 4
    elif ua_length <= 36:
        bigram_threshold = 6
    else:
        bigram_threshold = 8

    common_bigram_match = COMMON_BIGRAMS.findall(user_agent)

    return len(common_bigram_match) >= bigram_threshold


def reset_sequences(current: int, longest: int) -> tuple[int, int]:
    """
    Set longest sequence to current if it's shorter
    and reset current sequence to zero.
    """
    return 0, current if current > longest else longest


def uuid_like_name(value: str) -> bool:
    """
    Ensure that name isn't UUID-like string, such as:

    738FAAEF-30CF
    6BFAD903-A5EA-4E34
    5FAEB6ED-AE46-4A26-BA1B
    ea1866cb-c89a-6d5d-89b8-afdcdb715237
    """
    if not INTEGER.search(value):
        return False

    if UUID_LIKE_NAME.search(value) or LONG_UUID.search(value) or SHORT_UUID.search(value):
        return True

    # all sections of the string must contain an integer
    try:
        for group in TWO_SEGMENT_UUID.search(value).groups():
            if not INTEGER.search(group):
                return False
        return True
    except Exception:
        pass

    return False


def calculate_dtype(app_name: str) -> AppType:
    """
    For generic extractors try to return a more
    specific type we can be if reasonably sure.
    """
    app_name_lower = app_name.lower()
    for name, dtype in (
        ('update', AppType.DesktopApp),
        ('mail', AppType.PIM),
        ('api', AppType.Library),
        ('sdk', AppType.Library),
        ('webview', AppType.Browser),
    ):
        if name in app_name_lower:
            return dtype

    return AppType.Generic


__all__ = (
    'calculate_dtype',
    'ua_hash',
    'long_ua_no_punctuation',
    'only_numerals_and_punctuation',
    'mostly_numerals',
    'clean_ua',
    'mostly_repeating_characters',
    'random_alphanumeric_string',
    'uuid_like_name',
)
