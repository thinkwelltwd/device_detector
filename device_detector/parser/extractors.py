from ..lazy_regex import RegexLazyIgnore
from ..yaml_loader import app_custom_details
from device_detector.enums import AppType
from device_detector.utils import normalize_app_name

APP_ID_SANS_VERSION = RegexLazyIgnore(r'\b([a-z]{1,5}(?:\.[\w-]+){1,})')

# 6H4HRTU5E3.com.avast.osx.secureline.avastsecurelinehelper/47978 CFNetwork/976 Darwin/18.2.0 (x86_64)
# YMobile/1.0(com.kitkatandroid.keyboard/4.3.2;Android/6.0.1;lv1;LGE;LG-M153;;792x480
# x86_64; macOS 10.14.5 (18F132); com.apple.ap.adprivacyd; 143441-1,13
APP_ID_VERSION = RegexLazyIgnore(
    r'\b(?P<name>[a-z]{2,5}\.[\w\.\-]+)[;:/] ?(?P<version>[\d\.\-]+)\b'
)

# Match Application IDs like:
# FirebaseAuth.iOS/7.6.0 YanFlex.CPlus.Craigslist/5.1.6 iPhone/18.6 hw/iPhone15_3
# FirebaseAuth.iOS/8.4.0 depollsoft.pitchperfect/2.0.3 iPhone/18.4 hw/iPhone14_6
# but do not match domain names
LONG_PREFIX_APP_ID_VERSION = RegexLazyIgnore(
    r'[\s\(;:](?P<name>[a-z]{6,}\.[\w\.\-]{6,})[;:/] ?(?P<version>[\d\.\-]+)\b'
)


class ApplicationIDExtractor:
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

        _app_custom_details = app_custom_details()
        for app_id, version in app_ids:
            normalized_app_id = normalize_app_name(app_id)
            if custom_data := _app_custom_details.get(normalized_app_id.lower()):
                self.details = {
                    'name': custom_data['name'],
                    'app_id': normalized_app_id,
                    'version': version,
                    'type': custom_data['type'],
                }
                break
        else:
            self.details = {
                'app_id': normalize_app_name(app_ids[0][0]),
                'version': app_ids[0][1],
                'type': AppType.Generic,
            }

        return self

    def match_regexes(self) -> list[tuple[str, str]]:
        """
        Extract App IDs from the user agent.
        """
        # Skip UAs like sentry.java.android.react-native
        if self.user_agent.startswith('sentry.'):
            return []

        if app_ids := LONG_PREFIX_APP_ID_VERSION.findall(self.user_agent):
            return app_ids

        if app_ids := APP_ID_VERSION.findall(self.user_agent):
            return app_ids

        if app_ids := [(app_id, '') for app_id in APP_ID_SANS_VERSION.findall(self.user_agent)]:
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


__all__ = [
    'ApplicationIDExtractor',
]
