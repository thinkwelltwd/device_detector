from . import GenericClientParser

from ...lazy_regex import RegexLazyIgnore
from ..settings import SKIP_PREFIXES


# -------------------------------------------------------------------
# fmt: off
# Regexes that we use to parse UAs with a similar structure
parse_generic_regex = [
    # Weather_WeatherFoundation[1]_15E302
    # SpringBoard_WeatherFoundation[1]_16A
    (RegexLazyIgnore(r'(^(?:\w+)_WeatherFoundation).*'), 1),
    (RegexLazyIgnore(r'(^AVGSETUP).*'), 1),

    # ACC__14EDB170A0EAA78B40F
    (RegexLazyIgnore(r'(^ACC)__[A-Z0-9].*'), 1),

    # YWeather (iPhone/11.4.1; iOS; en_US;)
    # Mapbox iOS SDK (iPhone/11.1.1)
    # SCSDK/(iPhone;iOS;12.2)
    # Akamai NetSession C-API (win;AdDLMgr;capi_1.9.2;Vista)
    (RegexLazyIgnore(r'^([a-z0-9\- ]+)[ /]?\((?:iphone|ipad|win)'), 1),

    # CPIS&iPhone10.1&
    (RegexLazyIgnore(r'(^CPIS).*'), 1),

    # samsung SAMSUNG-SM-T337A SyncML_DM Client
    # samsung SMT377P SPDClient to samsung SM-T377P SPD-Client
    (RegexLazyIgnore(r'^samsung.*((?:SyncML_DM|SPD)[ \-]Client)$'), 1),
    (RegexLazyIgnore(r'(WXCommonUtils).*'), 1),

    # UBT_1EDA413E5BA1DEA76A
    # UBT_1ED
    (RegexLazyIgnore(r'^(UBT)_[\d\w]+$'), 1),

    # ACC10FDFFD20BCFEDA0D7D
    # ACC_4.00.3019_1BF78BFDF84E7EEFDA
    # ALU_1.02.3005_1EDDDB14FD0EBB93AE
    # ALU1023502106209EEF239E246AA
    # ALU__1023502106209EEF239E246AA
    (RegexLazyIgnore(r'^(ACC|ALU)_*[\d\w_\.]+$'), 1),

    # mShop:::Telly_iPhone_13.7.0:::iPad:::iPhone_OS_ == Telly_iPhone_13.7.0
    # mShop:::Amazon_Android_18.11.0.100:::SAMSUNG-SM-G935A:::Android_6.0.1
    # mShop:::WindowShop_Android_16.13.0.850:::SM-T817V:::Android_6.0.1
    (RegexLazyIgnore(r'^mshop:+([a-z0-9_\.]+)'), 1),
]

# -------------------------------------------------------------------
# Regexes that we use to extract app versions
extract_version_regex = [
    # ANVSDKv.5.0.21
    # ANVSDKv5.0.21
    (RegexLazyIgnore(r'(v?[\.\d]+$)')),

    # Catch versions with trailing, separated characters
    # AppNamev.5.0.21_PRC = v.5.0.21
    (RegexLazyIgnore(r'((?:v.?)?\d[\d\.]+)')),
]
# fmt: on


class WholeNameExtractor(GenericClientParser):
    """
    Catch all for user agents that do not use the slash format
    """

    __slots__ = ()

    parse_generic_regex = parse_generic_regex
    extract_version_regex = extract_version_regex

    # -------------------------------------------------------------------
    def _parse(self) -> None:
        if self.ch_client_data:
            return

        self.clean_name()

        if self.discard_name() or not self.is_name_length_valid():
            return

        self.parse_name_version()
        self.check_manual_appdetails()

        # WholeNameExtractor is called to supply secondary app data
        # if the Browser class matches. So if only Browser data was
        # found then there is no "secondary" data!
        if self.app_name.lower() in SKIP_PREFIXES:
            return

        app_details = self.appdetails_data
        code = self.app_name.lower().replace(' ', '')

        try:
            self.app_name = app_details[code]['name']
        except KeyError:
            pass

        self.ua_data = {
            'name': self.app_name,
            'version': self.app_version,
            'type': app_details[code].get('type', ''),
        }

        self.known = True

    def clean_name(self) -> None:
        """
        Check if the extracted name uses a known format that we can
        extract helpful info from.  If so, update ua data and mark
        as known.
        """
        for regex, group in self.parse_generic_regex:
            m = regex.match(self.user_agent)

            if m:
                try:
                    self.app_name = m.group(group).strip()
                    return
                except Exception:
                    continue

        self.app_name = self.user_agent

    def parse_name_version(self) -> str | None:
        """
        Check if app name has a suffix with the version number and
        extract if it does.  Return the UA string without the suffix.
        """
        for regex in self.extract_version_regex:
            match = regex.search(self.app_name)
            if match:
                self.app_version = match.group().strip()
                self.app_name = self.user_agent[: match.start()].strip(' /-')
                return self.app_version
        return None

    def is_name_length_valid(self) -> bool:
        """
        Check if app name portion of UA is between 3 and 60 chars
        """
        return 2 < len(self.app_name) <= 60
