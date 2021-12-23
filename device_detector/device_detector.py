from .lazy_regex import RegexLazyIgnore
import uuid

from .parser import (
    OS,

    # Devices
    Bot,
    Device,
    HbbTv,
    Notebook,
    ShellTv,
    MOBILE_DEVICE_TYPES,

    # Clients
    DictUA,
    Browser,
    FeedReader,
    Game,
    Library,
    MediaPlayer,
    Messaging,
    MobileApp,
    DesktopApp,
    P2P,
    PIM,
    VPNProxy,

    # Generic name extractors
    ApplicationIDExtractor,
    NameVersionExtractor,
    WholeNameExtractor,
    DESKTOP_OS,
)
from .settings import BOUNDED_REGEX, DDCache, WORTHLESS_UA_TYPES
from .utils import (
    clean_ua,
    long_ua_no_punctuation,
    mostly_numerals,
    mostly_repeating_characters,
    only_numerals_and_punctuation,
    ua_hash,
)
from .yaml_loader import RegexLoader

MAC_iOS = {
    'tvOS',
    'watchOS',
    'iOS',
    'Mac',
}

TOUCH_FRAGMENT = RegexLazyIgnore(BOUNDED_REGEX.format('Touch'))
TV_FRAGMENT = RegexLazyIgnore(BOUNDED_REGEX.format('Kylo|Espial|Opera TV Store|HbbTV'))
ANDROID_MOBILE_FRAGMENT = RegexLazyIgnore(BOUNDED_REGEX.format(r'Android( [\.0-9]+)?; Mobile;'))
ANDROID_TABLET_FRAGMENT = RegexLazyIgnore(BOUNDED_REGEX.format(r'Android( [\.0-9]+)?; Tablet;'))
CHROME_MOBILE_FRAGMENT = RegexLazyIgnore(BOUNDED_REGEX.format(r'Chrome/[\.0-9]* (?:Mobile|eliboM)'))
CHROME_NOTMOBILE_FRAGMENT = RegexLazyIgnore(BOUNDED_REGEX.format(r'Chrome/[\.0-9]* (?!Mobile)'))
# CHROME_MOBILE_FRAGMENT = RegexLazyIgnore(r'(?:Mobile|eliboM) Safari/')
# CHROME_NOTMOBILE_FRAGMENT = RegexLazyIgnore(r'(?!Mobile )Safari/')
DESKTOP_FRAGMENT = RegexLazyIgnore(BOUNDED_REGEX.format('Desktop (x(?:32|64)|WOW64);'))
OPERA_TABLET_FRAGMENT = RegexLazyIgnore(BOUNDED_REGEX.format('Opera Tablet'))

# Set max versioning to major version only (3, 5, 6, 200, 123)
VERSION_TRUNCATION_MAJOR = 0

# Set max versioning to minor version (3.4, 5.6, 6.234, 0.200, 1.23)
VERSION_TRUNCATION_MINOR = 1

# Set max versioning to path level (3.4.0, 5.6.344, 6.234.2, 0.200.3, 1.2.3)
VERSION_TRUNCATION_PATCH = 2

# set versioning to build number (3.4.0.12, 5.6.334.0, 6.234.2.3, 0.200.3.1, 1.2.3.0)
VERSION_TRUNCATION_BUILD = 3

# Set versioning to unlimited (no truncation)
VERSION_TRUNCATION_NONE = -1

VERSION_TRUNCATION_MAP = {
    'major': VERSION_TRUNCATION_MAJOR,
    'minor': VERSION_TRUNCATION_MINOR,
    'patch': VERSION_TRUNCATION_PATCH,
    'build': VERSION_TRUNCATION_BUILD,
    None: VERSION_TRUNCATION_NONE,
}


class DeviceDetector(RegexLoader):

    fixture_files = [
        'local/device/normalize.yml',
    ]

    CLIENT_PARSERS = (
        DictUA,
        FeedReader,
        Game,
        Messaging,
        MobileApp,
        MediaPlayer,
        P2P,
        PIM,
        VPNProxy,
        DesktopApp,
        Browser,
        Library,
        NameVersionExtractor,
        WholeNameExtractor,
    )

    DEVICE_PARSERS = (
        HbbTv,
        ShellTv,
        Notebook,
        Device,
    )

    def __init__(
        self,
        user_agent: str,
        skip_bot_detection: bool = False,
        skip_device_detection: bool = False,
        version_truncation: str = VERSION_TRUNCATION_NONE,
    ):
        """

        Args:
            user_agent: User Agent string to parse
            skip_bot_detection: Skip checking if client is a bot
            skip_device_detection: Skip device brand and model lookup.
            version_truncation: Set version truncation setting.
                None = '4.2.2', '34.0.1847.114'
                build = '4.2.2', '34.0.1847.114'
                patch = '4.2.2', '34.0.1847'
                minor = '4.2', '34.0'
                major = '4', '34'
        """

        super().__init__(version_truncation=version_truncation)
        # Holds the useragent that should be parsed
        self.user_agent = clean_ua(user_agent)
        self.ua_hash = ua_hash(self.user_agent)
        self._ua_spaceless = ''
        self.os = None
        self.client = None
        self.device = None
        self.model = None

        # Holds bot information if parsing the UA results in a bot
        # (All other information attributes will stay empty in that case)
        # If self.discardBotInformation is set to True, this property will be set to
        # True if parsed UA is identified as bot, additional information will be not available
        # If self.skip_bot_detection is set to True, bot detection will not be performed and
        # isBot will always be False
        self.bot = None

        self.skip_bot_detection = skip_bot_detection
        self.skip_device_detection = skip_device_detection
        self.all_details = {'normalized': ''}
        self.parsed = False

    @property
    def class_name(self) -> str:
        return self.__class__.__name__

    @property
    def ua_spaceless(self) -> str:
        if not self._ua_spaceless:
            self._ua_spaceless = self.user_agent.lower().replace(' ', '')
        return self._ua_spaceless

    def get_parse_cache(self):
        return DDCache['user_agents'].get(self.ua_hash, {}).get('parsed', {})

    def set_parse_cache(self):
        if not self.all_details:
            return self.all_details
        try:
            DDCache['user_agents'][self.ua_hash]['parsed'] = self.all_details
        except KeyError:
            DDCache['user_agents'][self.ua_hash] = {'parsed': self.all_details}
        return self

    # -----------------------------------------------------------------------------
    # UA parsing methods
    # -----------------------------------------------------------------------------
    def is_digit(self) -> bool:
        """
        Remove all punctuation. If only digits remain,
        don't bother saving, as nothing can be learned.

        21/4.35.1.2
        5.0.6

        Or if entire string is mostly numeric, discard
        15B93
        """
        if only_numerals_and_punctuation(self.user_agent):
            return True

        return mostly_numerals(self.user_agent)

    def is_uuid(self) -> bool:
        """
        Check for strings that are UUIDs

        (UUIDs enclosed in curly braces are valid)
        {1378F00B-BCEA-418F-B1AF-C343EA4F9417}
        {022CCD4D-EDE3-40EB-BE1D-FE4041B0A050}

        A:08338459-4ca1-457f-a596-94c3a9037d20
        I:5DFF6AEC-DCED-4BA0-B122-B1826C1CEB02
        """
        ua = self.user_agent
        if len(ua) >= 2 and ua[1] == ':':
            ua = self.user_agent[2:]

        try:
            uuid.UUID(ua)
            return True
        except (ValueError, AttributeError):
            return False

    def is_gibberish(self):
        """
        Check for frequently occurring patterns of meaninglessness
        """
        if mostly_repeating_characters(self.user_agent):
            return True

        return long_ua_no_punctuation(self.user_agent)

    def normalize(self):
        """
        Check for common worthless features that preclude the need for any further processing.

        If UA string is not worthless, process against normalizing regexes.

        Some client User Agent strings such as Antivirus services add file version information
        that is of no use outside the application itself. Remove such information to present a
        cleaner UA string with fewer duplicates
        """
        normalized = self.all_details.get('normalized', '')
        if normalized:
            return normalized

        if self.is_digit():
            self.all_details['normalized'] = 'Numeric'
        elif self.is_uuid():
            self.all_details['normalized'] = 'UUID'
        elif self.is_gibberish():
            self.all_details['normalized'] = 'Gibberish'
        else:
            for nr in self.normalized_regex_list:
                regex = nr['regex']
                groups = r'{}'.format(nr['groups'])
                ua = regex.sub(groups, self.user_agent)
                if ua != self.user_agent:
                    self.all_details['normalized'] = ua
                    break
            else:
                self.all_details['normalized'] = ''

        return self.all_details['normalized']

    def is_worthless(self):
        """
        Is this UA string of no possible interest?
        """
        self.normalize()
        return self.all_details['normalized'] in WORTHLESS_UA_TYPES

    def parse(self):
        self.all_details = self.get_parse_cache()
        if self.all_details:
            return self

        if not self.user_agent:
            return self

        if not self.skip_bot_detection:
            self.parse_bot()
            if self.is_bot():
                return self.set_parse_cache()

        if self.is_worthless():
            return self

        self.parse_os()
        self.parse_client()

        if not self.skip_device_detection:
            self.parse_device()

        return self.set_parse_cache()

    def supplement_secondary_client_data(self, app_idx):
        """
        Add data to secondary_client details
        """
        data = {
            'name': app_idx.pretty_name(),
            'version': app_idx.version(),
            'type': 'generic',
        }
        self.client.secondary_client.update(data)
        try:
            self.all_details['client']['secondary_client'].update(data)
        except KeyError:
            self.all_details['client']['secondary_client'] = data

    def parse_client(self) -> None:
        """
        Parses the UA for client information using the Client parsers
        """
        if self.client:
            return

        app_idx = ApplicationIDExtractor(self.user_agent)
        app_id = app_idx.extract().get('app_id', '')

        for Parser in self.CLIENT_PARSERS:
            parser = Parser(
                self.user_agent,
                self.ua_hash,
                self.ua_spaceless,
                self.VERSION_TRUNCATION,
            ).parse()

            if parser.ua_data:
                self.client = parser
                self.all_details['client'] = parser.ua_data
                self.all_details['client']['app_id'] = app_id
                if app_id:
                    if app_id in self.all_details['client']['name']:
                        self.all_details['client']['name'] = app_idx.pretty_name()
                    elif app_idx.override_name_with_app_id(client_name=parser.name()):
                        self.supplement_secondary_client_data(app_idx)
                return

        # if no client matched, still add name / app_id values
        if app_id:
            self.all_details['client'] = {
                'name': app_idx.pretty_name(),
                'app_id': app_id,
            }

    def parse_device(self) -> None:
        """
        Parses the UA for Device information using the Device or Bot parsers
        """
        if self.device or self.skip_device_detection:
            return

        for Parser in self.DEVICE_PARSERS:
            parser = Parser(
                self.user_agent,
                self.ua_hash,
                self.ua_spaceless,
                self.VERSION_TRUNCATION,
            ).parse()
            if parser.ua_data:
                self.device = parser
                self.all_details['device'] = parser.ua_data
                if self.all_details['device'] != 'desktop' and DESKTOP_FRAGMENT.search(
                        self.user_agent) is not None:
                    self.all_details['device']['device'] = 'desktop'
                return

    def parse_bot(self) -> None:
        """
        Parses the UA for bot information using the Bot parser
        """
        if not self.skip_bot_detection and not self.bot:
            self.bot = Bot(
                self.user_agent,
                self.ua_hash,
                self.ua_spaceless,
                self.VERSION_TRUNCATION,
            ).parse()
            self.all_details['bot'] = self.bot.ua_data

    def parse_os(self) -> None:
        """
        Parses the UA for Operating System information using the OS parser
        """
        if not self.os:
            self.os = OS(
                self.user_agent,
                self.ua_hash,
                self.ua_spaceless,
                self.VERSION_TRUNCATION,
            ).parse()
            self.all_details['os'] = self.os.ua_data

    # -----------------------------------------------------------------------------
    # Data post-processing / analysis
    # -----------------------------------------------------------------------------
    def is_known(self) -> bool:
        for section, data in self.all_details.items():
            if data:
                return True
        return False

    def is_bot(self) -> bool:
        return bool(self.all_details.get('bot'))

    def android_device_type(self) -> str:

        if self.os_name() != 'Android':
            return ''

        # Some user agents simply contain the fragment 'Android; Mobile;',
        # so we assume those devices as smartphones
        if ANDROID_MOBILE_FRAGMENT.findall(self.user_agent):
            return 'smartphone'

        # Chrome on Android passes the device type based on the keyword 'Mobile'
        # If it is present the device should be a smartphone, otherwise it's a tablet
        # See https://developer.chrome.com/multidevice/user-agent#chrome_for_android_user_agent
        if CHROME_MOBILE_FRAGMENT.search(self.user_agent) is not None:
            return 'smartphone'

        elif CHROME_NOTMOBILE_FRAGMENT.search(self.user_agent) is not None:
            return 'tablet'

        # Android up to 3.0 was designed for smartphones only. But as 3.0, which was tablet only,
        # was published too late, there were a bunch of tablets running with 2.x
        #
        # With 4.0 the two trees were merged and it is for smartphones and tablets
        # So were are expecting that all devices running Android < 2 are smartphones
        # Devices running Android 3.X are tablets. Device type of Android 2.X and 4.X+ are unknown
        os_version = self.os_version()
        if not os_version:
            return ''

        if str(os_version) < '2.0':
            return 'smartphone'

        if '3.0' <= str(os_version) < '4.0':
            return 'tablet'

        return ''

    def android_feature_phone(self) -> bool:
        """
        All detected feature phones running Android are more likely a smartphone
        """
        try:
            return self.device.dtype() == 'feature phone' and self.os.family() == 'Android'
        except AttributeError:
            pass

        return False

    def windows_tablet(self) -> bool:
        """
        According to http://msdn.microsoft.com/en-us/library/ie/hh920767(v=vs.85).aspx
        Internet Explorer 10 introduces the "Touch" UA string token. If this token is present
        at the end of the UA string, the computer has touch capability, and is running Windows 8
        (or later). This UA string will be transmitted on a touch-enabled system running
        Windows 8 (RT)

        As most touch enabled devices are tablets and only a smaller part are desktops/notebooks
        we assume that all Windows 8 touch devices are tablets.
        """
        touch_enabled = TOUCH_FRAGMENT.search(self.user_agent) is not None

        if touch_enabled and not self.device_model():
            return self.os_name() in ('Windows RT', 'Windows')

        return False

    def opera_tablet(self) -> bool:
        """
        Some UA strings contain 'Opera Tablet', so we assume those devices as tablets
        """
        return OPERA_TABLET_FRAGMENT.search(self.user_agent) is not None

    def is_television(self) -> bool:
        """Devices running Kylo or Espital TV Browsers are assumed to be a TV"""
        if self.client_name() in ('Kylo', 'Espial TV Browser'):
            return True
        return TV_FRAGMENT.search(self.user_agent) is not None

    def uses_mobile_browser(self) -> bool:
        try:
            if self.client.dtype() == 'browser':
                return self.client.is_mobile_only()
        except AttributeError:
            pass
        return False

    def engine(self) -> str:
        if 'browser' not in self.client_type():
            return ''
        return self.all_details.get('client', {}).get('engine', '')

    def is_mobile(self) -> bool:
        if self.device_type() in MOBILE_DEVICE_TYPES:
            return True
        return not self.is_bot() and not self.is_desktop() and not self.is_television()

    def is_desktop(self) -> bool:
        os_details = self.all_details.get('os') or {}
        os_name = os_details.get('name', '')

        if not os_name or os_name == 'Unknown':
            return False

        if self.uses_mobile_browser():
            return False

        return os_details.get('family', '') in DESKTOP_OS

    def client_name(self) -> str:
        return self.all_details.get('client', {}).get('name', '')

    def client_version(self) -> str:
        return self.all_details.get('client', {}).get('version', '')

    def client_type(self) -> str:
        return self.all_details.get('client', {}).get('type', '')

    def secondary_client_name(self) -> str:
        return self.all_details.get('client', {}).get('secondary_client', {}).get('name', '')

    def secondary_client_version(self) -> str:
        return self.all_details.get('client', {}).get('secondary_client', {}).get('version', '')

    def secondary_client_type(self) -> str:
        return self.all_details.get('client', {}).get('secondary_client', {}).get('type', '')

    def preferred_client_name(self):
        """
        Android and iOS mobile browsers often contain more interesting
        app information.

        If Secondary app can be extracted, prefer those app details
        as being more specific.
        """
        return self.secondary_client_name() or self.client_name()

    def preferred_client_version(self):
        return self.secondary_client_version() or self.client_version()

    def preferred_client_type(self):
        return self.secondary_client_type() or self.secondary_client_type()

    def device_type(self) -> str:
        """
        Get device type, preferably from the Device Parser, but
        calculate from other attributes Device Parser failed.

        Should work, even if skip_device_detection=True
        """
        if self.android_feature_phone():
            return 'smartphone'

        dt = self.all_details.get('device', {}).get('type', '')
        if dt:
            return dt

        aat = self.android_device_type()
        if aat:
            return aat

        if self.windows_tablet():
            return 'tablet'

        if self.is_television():
            return 'tv'

        if self.is_desktop():
            return 'desktop'

        if self.opera_tablet():
            return 'tablet'

        return ''

    def device_model(self) -> str:
        if self.skip_device_detection:
            return ''
        return self.all_details.get('device', {}).get('model', '')

    def device_brand(self) -> str:
        if self.skip_device_detection:
            return ''

        brand = self.all_details.get('device', {}).get('brand', '')
        if brand:
            return brand

        # Assume all devices running iOS / Mac OS are from Apple
        if self.os_name() in MAC_iOS:
            return 'Apple'

        return ''

    def os_name(self) -> str:
        return self.all_details.get('os', {}).get('name', '')

    def os_version(self) -> str:
        return self.all_details.get('os', {}).get('version', '')

    def pretty_name(self) -> str:
        return self.all_details.get('normalized') or self.user_agent

    def pretty_print(self) -> str:
        if not self.is_known():
            return self.user_agent
        os = client = device = 'N/A'
        if self.os_name():
            os = '{} {}'.format(self.os_name(), self.os_version())
        if self.client_name():
            client = '{} {} ({})'.format(
                self.client_name(),
                self.client_version(),
                self.client_type().title(),
            )
        if self.device_model():
            device = '{} ({})'.format(
                self.device_model(),
                self.device_type().title(),
            )
        return 'Client: {} Device: {} OS: {}'.format(client, device, os).strip()

    def __str__(self):
        return self.user_agent

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, self.user_agent)


class SoftwareDetector(DeviceDetector):

    def __init__(self, user_agent, skip_bot_detection=True, skip_device_detection=True):
        super().__init__(
            user_agent,
            skip_bot_detection=skip_bot_detection,
            skip_device_detection=skip_device_detection,
        )


__all__ = (
    'DeviceDetector',
    'SoftwareDetector',
    'VERSION_TRUNCATION_MAJOR',
    'VERSION_TRUNCATION_MINOR',
    'VERSION_TRUNCATION_PATCH',
    'VERSION_TRUNCATION_BUILD',
    'VERSION_TRUNCATION_NONE',
)
