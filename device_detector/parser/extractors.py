from ..lazy_regex import RegexLazyIgnore
from ..settings import BOUNDED_REGEX
from .settings import CHECK_PAIRS
from ..yaml_loader import RegexLoader, app_pretty_names_types_data

APP_ID = RegexLazyIgnore(r'\b([a-z]{2,5}\.[\w\d\.\-]+)')

# 6H4HRTU5E3.com.avast.osx.secureline.avastsecurelinehelper/47978 CFNetwork/976 Darwin/18.2.0 (x86_64)
# YMobile/1.0(com.kitkatandroid.keyboard/4.3.2;Android/6.0.1;lv1;LGE;LG-M153;;792x480
# x86_64; macOS 10.14.5 (18F132); com.apple.ap.adprivacyd; 143441-1,13
APP_ID_VERSION = RegexLazyIgnore(
    r'\b(?P<name>[a-z]{2,5}\.[\w\d\.\-]+)[;:/] ?(?P<version>[\d\.\-]+)\b'
)

# Dalvik/2.1.0 (Linux; U; Android 6.0.1; LG-M153 Build/MXB48T) [FBAN/AudienceNetworkForAndroid;FBSN/Android;FBSV/6.0.1;FBAB/com.outthinking.photo;FBAV/1.41;FBBV/37;FBVS/4.27.1;FBLC/en_US]
# Interested in the FBAB/<app.id> pattern
# i.e. FBAB/com.outthinking.photo
FACEBOOK_FRAGMENT = RegexLazyIgnore(BOUNDED_REGEX.format('FBAB/'))

# YHOO YahooMobile/1.0 (com.softacular.Sportacular; 7.10.1) (Apple; iPhone; iOS/11.4.1);
# YHOO YahooMobile/1.0 (com.aol.mapquest; 5.18.6) (Apple; iPhone; iOS/12.1.4);
YAHOO_FRAGMENT = RegexLazyIgnore(r'YHOO YahooMobile')

IGNORED_APP_IDS = {
    'com.yourcompany.testwithcustomtabs',
    'com.yourcompany.speedboxlite',
}


class DataExtractor:
    """
    Regex will define a string value or 1-based index
    position of the desired metadata

    - regex: '(?:Apple-)?(?:iPhone|iPad|iPod)(?:.*Mac OS X.*Version/(\\d+\\.\\d+)|; Opera)?'
      name: 'iOS'
      version: '$1'
    """

    __slots__ = (
        'metadata',
        'groups',
        'user_agent',
        'details',
        '_app_id_pretty_names',
    )

    # metadata value to extract / return
    # subclasses must override
    key = ''

    def __init__(self, metadata: dict, groups: tuple):
        """
        :param metadata: dict of regex and associated metadata
            {'regex': <regex1>, 'name': 'iOS', 'version': '$1'}
            {'regex': <regex2>, 'name': 'Windows', 'version': '10'}
        :param groups: Tuple of groups from regex
            ('Debian', None)
            ('iOS', '8_2')
        """
        self.metadata = metadata
        self.groups = groups

    def get_value_from_regex(self, value: str) -> str:
        """
        Model / Name values may be in format of
        $<int> or <NamePrefix> $<int>

        'Xino Z$1 X$2

        Replace %<int> section replaced with {} for format string

        'Xino Z$1 X$2 -> 'Xino Z{} X{}

        Return interpolated string with value from regex group
        """
        chars = []
        indices = []
        index_int_next = False

        for char in value:
            if char != '$':
                if index_int_next:
                    indices.append(int(char) - 1)
                    index_int_next = False
                else:
                    chars.append(char)
            else:
                chars.append('{}')
                index_int_next = True

        value = ''.join(chars)

        # collect regex group values, substituting empty string for None
        group_values = []
        for pos in indices:
            try:
                if not self.groups[pos]:
                    group_values.append('')
                else:
                    group_values.append(self.groups[pos])
            except IndexError:
                return ''

        return value.format(*group_values).strip()

    def extract(self) -> str:
        value = str(self.metadata.get(self.key, ''))
        if value and '$' in value:
            return self.get_value_from_regex(value)
        return value

    def __str__(self) -> str:
        return f'{self.__class__.__name__} Extractor'

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.metadata}, {self.groups})'


class ApplicationIDExtractor(RegexLoader):
    """
    Extract App Store IDs such as:

    extract APP IDs such as
    com.cloudveil.CloudVeilMessenger
    com.houzz.app
    com.google.Maps
    """

    key = 'app_id'

    def __init__(self, user_agent: str) -> None:
        self.user_agent = user_agent
        self.details: dict[str, str] = {}
        self._app_id_pretty_names = app_pretty_names_types_data()

    def override_name_with_app_id(self, client_name: str) -> bool:
        """
        Override the parsed name with the AppID / BundleID.

        Useful when application connects with API service where
        both App ID and service API data are included in the same UA.
        """
        if client_name in CHECK_PAIRS:
            return True

        for REGEX in (
            FACEBOOK_FRAGMENT,
            YAHOO_FRAGMENT,
        ):
            if REGEX.search(self.user_agent) is not None:
                return True

        return False

    def extract(self) -> dict:
        """
        Parse for

        "<tld>.<string.<string>.<string><sep><version>" or
        "<tld>.<string.<string>.<string>"

        In the (unlikely) event that multiple valid IDs
        are found, just return the first one.
        """
        if self.details:
            return self.details

        app_ids = APP_ID_VERSION.findall(self.user_agent)
        if not app_ids:
            app_ids = [(app_id, '') for app_id in APP_ID.findall(self.user_agent)]

        scrubbed_app_ids = [
            (app_id.lower(), version)
            for app_id, version in app_ids
            if app_id.lower() not in IGNORED_APP_IDS
        ]
        if not scrubbed_app_ids:
            return {}

        for app_id, version in scrubbed_app_ids:
            app_id_lower = app_id.lower()
            if app_id_lower in IGNORED_APP_IDS:
                continue
            if pretty_name := self._app_id_pretty_names.get(app_id_lower):
                self.details = {
                    'name': pretty_name['name'],
                    'app_id': app_id,
                    'version': version,
                }
                break
        else:
            self.details = {
                'app_id': scrubbed_app_ids[0][0],
                'version': scrubbed_app_ids[0][1],
            }

        return self.details

    def version(self) -> str:
        return self.details.get('version', '')

    def pretty_name(self) -> str:
        details = self.extract()

        if name := self.details.get('name', ''):
            return name

        if not details:
            return ''

        app_id = details.get('app_id', '')
        # If it might be a domain name, then return the app_id as-is
        if not app_id or not app_id.startswith(('com.', 'au.com.')):
            return app_id

        self.details['name'] = ' '.join(app_id.split('.')[1:]).title()

        return self.details['name']

    def __str__(self) -> str:
        return f'{self.__class__.__name__}("{self.user_agent}")'

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}("{self.user_agent}")'


class NameExtractor(DataExtractor):
    key = 'name'


class ModelExtractor(DataExtractor):
    key = 'model'

    def extract(self) -> str:
        value = super().extract()
        if not value:
            return value

        if value == 'Build':
            return ''

        # normalize D510_TD / ETON-T730D_TD
        if value.endswith('_TD'):
            value = value[:-3]
        return value.replace('_', ' ').strip()


class VersionExtractor(DataExtractor):
    key = 'version'

    def extract(self) -> str:
        value = super().extract()
        if not value:
            return value

        return value.replace('_', '.').strip('.')


__all__ = (
    'ApplicationIDExtractor',
    'DataExtractor',
    'ModelExtractor',
    'NameExtractor',
    'VersionExtractor',
)
