from ..lazy_regex import RegexLazyIgnore
from ..yaml_loader import RegexLoader, app_pretty_names_types_data
from device_detector.enums import AppType

APP_ID = RegexLazyIgnore(r'\b([a-z]{2,5}\.[\w\d\.\-]+)')
GOOGLE_APPS = RegexLazyIgnore(r'(com\.google\.\w+)\.\w+$')

# 6H4HRTU5E3.com.avast.osx.secureline.avastsecurelinehelper/47978 CFNetwork/976 Darwin/18.2.0 (x86_64)
# YMobile/1.0(com.kitkatandroid.keyboard/4.3.2;Android/6.0.1;lv1;LGE;LG-M153;;792x480
# x86_64; macOS 10.14.5 (18F132); com.apple.ap.adprivacyd; 143441-1,13
APP_ID_VERSION = RegexLazyIgnore(
    r'\b(?P<name>[a-z]{2,5}\.[\w\d\.\-]+)[;:/] ?(?P<version>[\d\.\-]+)\b'
)

# Match Application IDs like:
# YanFlex.CPlus.Craigslist
# depollsoft.pitchperfect
# but do not match domain names
LONG_PREFIX_APP_ID_VERSION = RegexLazyIgnore(
    r' (?P<name>[a-z]{6,}\.[\w\d\.\-]{6,})[;:/] ?(?P<version>[\d\.\-]+)\b'
)


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

        'Xino Z$1 X$2 -> 'Xino Z{} X{}'

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

        fmt_string = ''.join(chars)
        return fmt_string.format(*group_values).strip()

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

    def extract(self) -> 'ApplicationIDExtractor':
        """
        Parse for

        "<tld>.<string.<string>.<string><sep><version>" or
        "<tld>.<string.<string>.<string>"

        In the (unlikely) event that multiple valid IDs
        are found, just return the first one.
        """
        if self.details:
            return self

        if not (app_ids := self.match_regexes()):
            return self

        pretty_names = self._app_id_pretty_names
        for app_id, version in app_ids:
            if pretty_name := pretty_name_from_app_id(app_id.lower(), pretty_names):
                self.details = {
                    'name': pretty_name['name'],
                    'app_id': app_id,
                    'version': version,
                    'type': pretty_name['type'],
                }
                break
        else:
            self.details = {
                'app_id': app_ids[0][0],
                'version': app_ids[0][1],
                'type': AppType.Generic,
            }

        return self

    def match_regexes(self) -> list[tuple[str, str]]:
        """
        Extract App IDs from the user agent.
        """
        if app_ids := LONG_PREFIX_APP_ID_VERSION.findall(self.user_agent):
            return app_ids

        if app_ids := APP_ID_VERSION.findall(self.user_agent):
            return app_ids

        if app_ids := [(app_id, '') for app_id in APP_ID.findall(self.user_agent)]:
            return app_ids

        return []

    def version(self) -> str:
        return self.details.get('version', '')

    def pretty_name(self) -> str:
        return self.details.get('name', '')

    def __str__(self) -> str:
        return f'{self.__class__.__name__}({self.user_agent!r})'

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.user_agent!r})'


def pretty_name_from_app_id(app_id: str, pretty_names: dict) -> dict:
    """
    Normalize app id before looking up the value, to avoid
    storing variations for values like:

    com.google.Drive.ExtensionFramework
    com.google.Drive.ShareExtension
    com.google.Drive.FileProviderExtension
    com.google.photos.ModuleFramework
    """
    if matched := GOOGLE_APPS.match(app_id):
        if pn := pretty_names.get(matched.group(1)):
            return pn

    return pretty_names.get(app_id) or {}


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
