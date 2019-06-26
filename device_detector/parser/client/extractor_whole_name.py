from . import GenericClientParser
try:
    import regex as re
except (ImportError, ModuleNotFoundError):
    import re

from ..settings import SKIP_PREFIXES
from ...settings import DDCache


class WholeNameExtractor(GenericClientParser):
    """
    Catch all for user agents that do not use the slash format
    """

    # -------------------------------------------------------------------
    # Regexes that we use to parse UAs with a similar structure
    parse_generic_regex = [
        # Weather_WeatherFoundation[1]_15E302
        # SpringBoard_WeatherFoundation[1]_16A
        (re.compile(r'(^(?:\w+)_WeatherFoundation).*', re.IGNORECASE), 1),
        (re.compile(r'(^AVGSETUP).*', re.IGNORECASE), 1),

        # ACC__14EDB170A0EAA78B40F
        (re.compile(r'(^ACC)__[A-Z0-9].*'), 1),

        # YWeather (iPhone/11.4.1; iOS; en_US;)
        # Mapbox iOS SDK (iPhone/11.1.1)
        # SCSDK/(iPhone;iOS;12.2)
        # Akamai NetSession C-API (win;AdDLMgr;capi_1.9.2;Vista)
        (re.compile(r'^([a-z0-9\- ]+)[ /]?\((?:iphone|ipad|win)', re.IGNORECASE), 1),

        # CPIS&iPhone10.1&
        (re.compile(r'(^CPIS).*', re.IGNORECASE), 1),

        # samsung SAMSUNG-SM-T337A SyncML_DM Client
        # samsung SMT377P SPDClient to samsung SM-T377P SPD-Client
        (re.compile(r'^samsung.*((?:SyncML_DM|SPD)[ \-]Client)$', re.IGNORECASE), 1),
        (re.compile(r'(WXCommonUtils).*', re.IGNORECASE), 1),

        # mShop:::Telly_iPhone_13.7.0:::iPad:::iPhone_OS_ == Telly_iPhone_13.7.0
        # mShop:::Amazon_Android_18.11.0.100:::SAMSUNG-SM-G935A:::Android_6.0.1
        # mShop:::WindowShop_Android_16.13.0.850:::SM-T817V:::Android_6.0.1
        (re.compile(r'^mshop:+([a-z0-9_\.]+)', re.IGNORECASE), 1),
    ]

    # -------------------------------------------------------------------
    # Regexes that we use to extract app versions
    extract_version_regex = [
        # ANVSDKv.5.0.21
        # ANVSDKv5.0.21
        (re.compile(r'(v?[\.\d]+$)', re.IGNORECASE)),

        # Catch versions with trailing, separated characters
        # AppNamev.5.0.21_PRC = v.5.0.21
        (re.compile(r'((?:v.?)?\d[\d\.]+)', re.IGNORECASE)),
    ]

    # -------------------------------------------------------------------
    def _parse(self):

        self.clean_name()

        if self.discard_name() or not self.is_name_length_valid():
            return

        self.parse_name_version()
        self.normalize_app_name()

        # WholeNameExtractor is called to supply secondary app data
        # if the Browser class matches. So if only Browser data was
        # found then there is no "secondary" data!
        if self.app_name.lower() in SKIP_PREFIXES:
            return

        self.ua_data = {
            'name': self.app_name,
            'version': self.app_version,
        }

        self.known = True

    def parse_name_version(self) -> str:
        """
        Check if app name has a suffix with the version number and
        extract if it does.  Return the UA string without the suffix.
        """
        for regex in self.extract_version_regex:

            match = regex.search(self.app_name)
            if match:
                self.app_version = match.group().strip()
                self.app_name = self.user_agent[:match.start()].strip(' /-')
                return self.app_version

    def normalize_app_name(self):
        """
        If this name was specified in App Details, lookup
        the dtype and normalized name.
        """
        name_lower = self.app_name.lower().replace(' ', '')
        for dtype, details in DDCache['appdetails'].items():
            if name_lower in details:
                self.calculated_dtype = dtype
                self.app_name = details[name_lower]['name']

    def is_name_length_valid(self) -> bool:
        """
        Check if app name portion of UA is between 3 and 60 chars
        """
        return 2 < len(self.app_name) <= 60
