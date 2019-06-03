from . import GenericClientParser
try:
    import regex as re
except (ImportError, ModuleNotFoundError):
    import re

from ...settings import DDCache


class WholeNameExtractor(GenericClientParser):
    """
    Catch all for user agents that do not use the slash format
    """

    # -------------------------------------------------------------------
    # Regexes that we use to parse UA's with a similar structure
    parse_generic_regex = [
        # Weather_WeatherFoundation[1]_15E302
        # SpringBoard_WeatherFoundation[1]_16A
        (re.compile(r'(^(?:\w+)_WeatherFoundation).*', re.IGNORECASE), 1),
        (re.compile(r'(^AVGSETUP).*', re.IGNORECASE), 1),

        # samsung SAMSUNG-SM-T337A SyncML_DM Client
        # samsung SMT377P SPDClient to samsung SM-T377P SPD-Client
        (re.compile(r'^samsung.*((?:SyncML_DM|SPD)[ \-]Client)$', re.IGNORECASE), 1),
        (re.compile(r'(WXCommonUtils).*', re.IGNORECASE), 1),
    ]

    # -------------------------------------------------------------------
    # Regexes that we use to extract app versions
    extract_version_regex = [
        (re.compile(r'(v?[\.\d]+$)', re.IGNORECASE)),
    ]

    # -------------------------------------------------------------------
    def _parse(self):
        if '/' in self.user_agent:
            return

        self.app_name = self.extract_version_suffix().strip()

        if self.discard_name() or not self.is_name_length_valid():
            return

        self.clean_name()

        self.ua_data = {
            'name': self.app_name,
            'version': self.app_version,
        }

        self.known = True

    def extract_version_suffix(self) -> str:
        """
        Check if app name has a suffix with the version number and
        extract if it does.  Return the UA string without the suffix.
        """

        for regex in self.extract_version_regex:

            match = regex.search(self.user_agent)
            if match:
                self.app_version = match.group()
                name = self.user_agent[:match.start()]
                break
        else:
            name = self.user_agent

        # if this name was specified in App Details, lookup
        # the dtype and normalized name.
        name_lower = name.lower().replace(' ', '')
        for dtype, details in DDCache['appdetails'].items():
            if name_lower in details:
                self.calculated_dtype = dtype
                return details[name_lower]['name']

        return name

    def is_name_length_valid(self) -> bool:
        """
        Check if app name portion of UA is between 3 and 60 chars
        """
        return 2 < len(self.app_name) <= 60
