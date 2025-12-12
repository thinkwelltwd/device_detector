import regex
from typing import cast, TypedDict
from device_detector.enums import DeviceType, AppType
from ..lazy_regex import RegexLazyIgnore
from ..yaml_loader import app_pretty_names_types_data
from .settings import CLIENT_HINT_TO_APP_MAP, FAMILY_FROM_OS, BROWSER_TO_ABBREV


CH_UA = RegexLazyIgnore(r'^"([^"]+)"; ?v="([^"]+)"(?:, )?')
TV_APP = RegexLazyIgnore(r'tv\.?(browser|firefox|search|web)')
CHROMIUM_BASED_BROWSERS = frozenset((
    'Chromium',
    'Chrome Webview',
    'Microsoft Edge',
    'Microsoft Edge Simulate',
))


class ClientHintsHeader(TypedDict):
    platform: str
    platform_version: str
    full_version: str
    full_version_list: str | dict
    mobile: bool
    architecture: str
    bitness: str
    model: str
    form_factors: set[str]
    app: str


# "Chromium";v="106", "Brave";v="106", "Not;A=Brand";v="99"
# "Not_A Brand";v="8.0.0.0", "Chromium";v="120.0.6099.115", "Google Chrome";v="120.0.6099.115"
# NOT_A_BRAND = {
#     'not;a=brand',
#     'not:a-brand',
#     'not_a brand',
#     'not?a_brand',
#     'not-a.brand',
#     'not(a:brand',
#     'not.a/brand',
#     'not a;brand',
#     ';not a brand',
#     'not=a?brand',
# }

# Normalize forms "Not:A-Brand"
NOT_A_BRAND = regex.compile(r"[^\w\s\']|_| ")
NOT_A_BRAND_FRAGMENT = 'notabrand'


# https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Sec-CH-UA-Form-Factors
MOBILE_FORM_FACTORS = {
    'Mobile',
    'Tablet',
    'EInk',
    'Watch',
}


class ClientHints:
    __slots__ = (
        'platform',
        'platform_version',
        'full_version',
        'full_version_list',
        'mobile',
        'architecture',
        'bitness',
        'model',
        'form_factors',
        'app',
        'headers',
        'client_hints_map',
        '_browser_data',
        '_client_data',
        '_client_name',
        'app_pretty_names',
        '_calculated_app_type',
    )

    def __init__(
        self,
        platform: str,
        platform_version: str,
        full_version: str,
        full_version_list: str | dict,
        mobile: bool,
        architecture: str,
        bitness: str,
        model: str,
        form_factors: set[str],
        app: str,
    ):
        # fmt: off
        self.platform = platform                     # Sec-CH-UA-Platform
        self.platform_version = platform_version     # Sec-CH-UA-Platform-Version
        self.full_version = full_version             # Sec-CH-UA-Full-Version
        self.full_version_list = full_version_list   # Sec-CH-UA-Full-Version-List
        self.mobile = mobile                         # Sec-CH-UA-Mobile
        self.architecture = architecture             # Sec-CH-UA-Arch
        self.bitness = bitness                       # Sec-CH-UA-Bitness
        self.model = model                           # Sec-CH-UA-Model
        self.form_factors = form_factors             # Sec-CH-UA-Form-Factors
        self.app = app                               # X-Requested-With
        # fmt: on

        self.headers: dict[str, str] = {}
        self.client_hints_map: dict[str, str] = {}

        self._browser_data: dict | None = None
        self._client_data: dict | None = None
        self._client_name = ''
        self.app_pretty_names = app_pretty_names_types_data()

        # Set from pretty name fixtures, or other Header / UA attributes
        # If this value isn't set, then
        self._calculated_app_type = AppType.Unknown

    def __str__(self) -> str:
        return (
            f'Client: {self.client_name()} '
            f'Platform: {self.platform} ({self.platform_version}) '
            f'Architecture: {self.architecture} ({self.bitness})'
        )

    @classmethod
    def new(cls, headers: dict) -> 'ClientHints':
        """
        Generate class from HTTP headers.
        """
        params = ClientHintsHeader(
            platform='',
            platform_version='',
            full_version='',
            full_version_list='',
            mobile=False,
            architecture='',
            bitness='',
            model='',
            form_factors=set(),
            app='',
        )

        # fmt: off
        for header_key, value in headers.items():
            key = header_key.lower().replace('_', '-')
            value = value or ''
            match key:
                case (
                    'sec-ch-ua-arch'
                    | 'http-sec-ch-ua-arch'
                    | 'architecture'
                ):
                    params['architecture'] = value.strip('"')

                case (
                    'sec-ch-ua-bitness'
                    | 'http-sec-ch-ua-bitness'
                    | 'bitness'
                ):
                    params['bitness'] = value.strip('"')

                case (
                    'sec-ch-ua-mobile'
                    | 'http-sec-ch-ua-mobile'
                    | 'mobile'
                ):
                    params['mobile'] = value.strip('"')

                case (
                    'sec-ch-ua-model'
                    | 'http-sec-ch-ua-model'
                    | 'model'
                ):
                    params['model'] = value.strip('"')

                # "Brave";v="139"
                case (
                    'sec-ch-ua-full-version'
                    | 'http-sec-ch-ua-full-version'
                    | 'uafullversion'
                    | 'full_version'
                ):
                    params['full_version'] = value.strip('"')

                case (
                    'sec-ch-ua-platform'
                    | 'http-sec-ch-ua-platform'
                    | 'platform'
                ):
                    platform = value.strip('"')
                    params['platform'] = FAMILY_FROM_OS.get(platform, platform)

                case (
                    'sec-ch-ua-platform-version'
                    | 'http-sec-ch-ua-platform-version'
                    | 'platformversion'
                    | 'full_version'
                ):
                    params['platform_version'] = value.strip('"')

                # Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"
                case (
                    'sec-ch-ua-full-version-list'
                    | 'http-sec-ch-ua-full-version-list'
                    | 'full_version_list'
                ):
                    params['full_version_list'] = value

                case 'brands':
                    if not params['full_version_list']:
                        params['full_version_list'] = from_ch_list(value)

                # use this only if no other header already set the list
                case 'fullversionlist':
                    if not params['full_version_list'] or 'brands' in headers:
                        params['full_version_list'] = from_ch_list(value)

                case (
                    'sec-ch-ua'
                    | 'http-sec-ch-ua'
                ):
                    # Don't overwrite full version details truncated version!
                    # " Not A;Brand";v="99.0.0.0", "Chromium";v="98.0.4758.82", "Opera";v="98.0.4758.82"
                    # Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"
                    if not params['full_version_list']:
                        params['full_version_list'] = value.strip()

                case (
                    'x-requested-with'
                    | 'http-x-requested-with'
                ):
                    if not value.lower().startswith(('xmlhttprequest', 'fetch')):
                        params['app'] = value.strip('"')

                case (
                    'http-sec-ch-ua-form-factors'
                    | 'sec-ch-ua-form-factors' | 'form_factors'
                ):
                    if isinstance(value, (list, set, tuple)):
                        params['form_factors'] = set(value)
                    else:
                        params['form_factors'] = {ff.strip(' "') for ff in value.split(',')}
        # fmt: on

        ch = ClientHints(**params)
        ch.headers = headers
        ch.client_hints_map = from_ch_ua(ch.full_version_list)

        return ch

    def client_name(self) -> str:
        """
        Extract most likely client name from the UA.

        "Not;A=Brand";v="99", "Brave";v="139", "Chromium";v="139"
        """
        if not self._client_name:
            if client_name := self._get_pretty_name(self.app):
                return client_name

            name = extract_name_from_hints(self.client_hints_map)

            # If the name has a "pretty name" override defined
            # use that name & type.
            if not self._calculated_app_type:
                if pretty_name := self._get_pretty_name(name.lower().replace(' ', '')):
                    return pretty_name

            name_lower = name.lower()
            if name_lower in BROWSER_TO_ABBREV:
                self._calculated_app_type = AppType.Browser
            else:
                # Strip "Browser" suffix from browsers such as "Brave Browser"
                # and "CCleaner Browser" per their official name
                if name.endswith(' Browser'):
                    if name_lower[:-8] in BROWSER_TO_ABBREV:
                        name = name[:-8]
                        self._calculated_app_type = AppType.Browser
                elif f'{name_lower} browser' in BROWSER_TO_ABBREV:
                    name = f'{name} Browser'
                    self._calculated_app_type = AppType.Browser

            self._client_name = name

        return self._client_name

    def _get_pretty_name(self, app_name: str) -> str:
        """
        If a fixture defines a "pretty name" for this brand name,
        then set that name and app type.
        """
        if app_name and (app_pretty_name := self.app_pretty_names.get(app_name)):
            self._client_name = app_pretty_name['name']
            self._calculated_app_type = cast(AppType, app_pretty_name['type'])
            return self._client_name
        return ''

    def client_version(self) -> str:
        return self.client_hints_map.get(self.client_name(), '')

    def client_is_browser(self) -> bool:
        return self.client_data().get('type') == AppType.Browser

    def is_mobile(self) -> bool:
        """
        Sec-CH-UA-Mobile
        https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Sec-CH-UA-Mobile
        """
        if self.mobile == '?1':
            return True

        if not self.form_factors:
            return False

        return MOBILE_FORM_FACTORS.issubset(self.form_factors)

    def is_desktop(self) -> bool:
        return self.mobile == '?0' or 'Desktop' in self.client_hints_map

    def is_running_android(self) -> bool:
        return self.mobile == 'Android'

    def is_television(self) -> bool:
        if not self.app:
            return False
        return TV_APP.search(self.app) is not None

    def app_type(self) -> AppType:
        return self._calculated_app_type

    def device_type(self) -> DeviceType | None:
        if self.is_television():
            return DeviceType.TV
        elif self.is_desktop():
            return DeviceType.Desktop
        elif self.is_mobile():
            if 'Tablet' in self.form_factors or 'EInk' in self.form_factors:
                return DeviceType.Tablet
            return DeviceType.Smartphone
        return None

    def client_data(self) -> dict:
        """
        Get dictionary of all client data that can
        be extracted from client hints headers.
        """
        if self._client_data is None:
            ch_data = {}

            if name := self.client_name():
                ch_data['name'] = name
            if app_id := self.app:
                ch_data['app_id'] = app_id

            if name or app_id:
                if app_type := self.app_type():
                    ch_data['type'] = app_type
                if version := self.client_version():
                    ch_data['version'] = version
                if abbrev := BROWSER_TO_ABBREV.get(name.lower()):
                    ch_data['short_name'] = abbrev

            self._client_data = ch_data

        return self._client_data or {}

    def os_data(self) -> dict:
        """
        Get dictionary of all OS data that can
        be extracted from client hints headers.
        """
        ch_data = {}

        if platform := self.platform:
            ch_data['platform'] = platform
        if platform_version := self.platform_version:
            ch_data['platform_version'] = platform_version

        return ch_data


def from_ch_ua(ua: str | dict) -> dict:
    """
    Extract values from Client Hint User Agent.

    "Not;A=Brand";v="99", "Brave";v="139", "Chromium";v="139"
    """
    if isinstance(ua, dict):
        return ua

    ch_map = {}
    for segment in ua.split(', '):
        if ch := CH_UA.findall(segment):
            name = ch[0][0]
            if NOT_A_BRAND.sub('', name.lower().strip()) == NOT_A_BRAND_FRAGMENT:
                continue
            dd_name = CLIENT_HINT_TO_APP_MAP.get(name, name)
            ch_map[dd_name] = ch[0][1]

    return ch_map


def from_ch_list(ch: list) -> dict:
    """
    Extract values from Client Hints when it's list of dicts.

    [
        {'brand': 'Not_A Brand', 'version': '8'},
        {'brand': 'Chromium', 'version': '120'},
    ]
    """
    ch_map = {}

    for header in ch:
        brand = header['brand']
        if NOT_A_BRAND.sub('', brand.lower().strip()) == NOT_A_BRAND_FRAGMENT:
            continue
        dd_name = CLIENT_HINT_TO_APP_MAP.get(brand, brand)
        ch_map[dd_name] = header['version']

    return ch_map


def extract_name_from_hints(hints: dict) -> str:
    """
    Extract most specific name from client hints.
    """

    for client_name in hints:
        # If we detected a brand, that is not Chromium, we will use it,
        # otherwise we will look further
        if client_name not in CHROMIUM_BASED_BROWSERS:
            return client_name

    name = ''
    for client_name in hints:
        name = client_name
        if client_name != 'Chromium':
            break

    return name
