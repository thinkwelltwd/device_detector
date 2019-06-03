try:
    import regex as re
except (ImportError, ModuleNotFoundError):
    import re
import uuid

from .parser import (
    OS,

    # Devices
    Bot,
    Device,
    MOBILE_DEVICE_TYPES,

    # Clients
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
)
from .settings import DDCache, WORTHLESS_UA_TYPES
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
    'ATV',
    'IOS',
    'MAC',
}


class DeviceDetector(RegexLoader):

    fixture_files = [
        'local/device/normalize.yml',
    ]

    CLIENT_PARSERS = (
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

    DEVICE_PARSERS = [
        Device,
    ]

    def __init__(self, user_agent, skip_bot_detection=False, skip_device_detection=False):

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
        self.touch_fragment = re.compile(r'Touch', re.IGNORECASE)
        self.TV_fragment = re.compile(r'Kylo|Espial|Opera TV Store|HbbTV', re.IGNORECASE)
        self.facebook_fragment = re.compile(f'FBAB/', re.IGNORECASE)

        if self.ua_hash not in DDCache['user_agents']:
            DDCache['user_agents'][self.ua_hash] = {}

    @property
    def class_name(self) -> str:
        return self.__class__.__name__

    @property
    def ua_spaceless(self) -> str:
        if not self._ua_spaceless:
            self._ua_spaceless = self.user_agent.lower().replace(' ', '')
        return self._ua_spaceless

    def get_parse_cache(self):
        return DDCache['user_agents'][self.ua_hash].get('parsed', None)

    def set_parse_cache(self):
        try:
            DDCache['user_agents'][self.ua_hash]['parsed'] = self
        except KeyError:
            DDCache['user_agents'][self.ua_hash] = {'parsed': self}
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
        if self.all_details['normalized']:
            return self.all_details['normalized']

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

        return self.all_details['normalized']

    def is_worthless(self):
        """
        Is this UA string of no possible interest?
        """
        self.normalize()
        return self.all_details['normalized'] in WORTHLESS_UA_TYPES

    def parse(self):
        parsed = self.get_parse_cache()
        if parsed:
            return parsed

        if not self.user_agent:
            return self

        if not self.skip_bot_detection:
            self.parse_bot()
            if self.is_bot():
                return self

        if self.is_worthless():
            return self

        self.parse_os()
        self.parse_client()

        if not self.skip_device_detection:
            self.parse_device()

        return self.set_parse_cache()

    def parse_client(self) -> None:
        """
        Parses the UA for client information using the Client parsers
        """
        if self.client:
            return

        app_idx = ApplicationIDExtractor(self.user_agent)
        app_id = app_idx.extract().get('app_id', '')

        for Parser in self.CLIENT_PARSERS:
            parser = Parser(self.user_agent, self.ua_hash, self.ua_spaceless).parse()
            if parser.ua_data:
                self.client = parser
                self.all_details['client'] = parser.ua_data
                self.all_details['client']['app_id'] = app_id
                if app_id:
                    if app_id in self.all_details['client']['name']:
                        self.all_details['client']['name'] = app_idx.pretty_name()
                    elif self.is_facebook_tracking_noise():
                        self.all_details['client']['name'] = app_idx.pretty_name()
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
            parser = Parser(self.user_agent, self.ua_hash, self.ua_spaceless).parse()
            if parser.ua_data:
                self.device = parser
                self.all_details['device'] = parser.ua_data
                return

    def parse_bot(self) -> None:
        """
        Parses the UA for bot information using the Bot parser
        """
        if not self.skip_bot_detection and not self.bot:
            self.bot = Bot(self.user_agent, self.ua_hash, self.ua_spaceless).parse()
            self.all_details['bot'] = self.bot.ua_data

    def parse_os(self) -> None:
        """
        Parses the UA for Operating System information using the OS parser
        """
        if not self.os:
            self.os = OS(self.user_agent, self.ua_hash, self.ua_spaceless).parse()
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
        if not self.bot:
            return False
        return self.bot.is_known()

    def ambiguous_android_type(self) -> str:
        """
        Android up to 3.0 was designed for smartphones only. But as 3.0, which was tablet only,
        was published too late, there were a bunch of tablets running with 2.x

        With 4.0 the two trees were merged and it is for smartphones and tablets
        So were are expecting that all devices running Android < 2 are smartphones
        Devices running Android 3.X are tablets. Device type of Android 2.X and 4.X+ are unknown
        """
        if self.os_short_name() != 'AND':
            return ''

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
        touch_enabled = self.touch_fragment.search(self.user_agent) is not None

        if touch_enabled and not self.device_model():
            return self.os_short_name() in ('WRT', 'WIN')

        return False

    def is_television(self) -> bool:
        """Devices running Kylo or Espital TV Browsers are assumed to be a TV"""
        if self.client_name() in ('Kylo', 'Espial TV Browser'):
            return True
        return self.TV_fragment.search(self.user_agent) is not None

    def uses_mobile_browser(self) -> bool:
        try:
            if self.client.dtype() == 'browser':
                return self.client.is_mobile_only()
        except AttributeError:
            pass
        return False

    def is_facebook_tracking_noise(self):
        """
        Dalvik/2.1.0 (Linux; U; Android 6.0.1; LG-M153 Build/MXB48T) [FBAN/AudienceNetworkForAndroid;FBSN/Android;FBSV/6.0.1;FBAB/com.outthinking.photo;FBAV/1.41;FBBV/37;FBVS/4.27.1;FBLC/en_US]
        Interested in the FBAB/<app.id> pattern
        i.e. FBAB/com.outthinking.photo
        """
        return self.facebook_fragment.search(self.user_agent) is not None

    def engine(self) -> str:
        if 'browser' not in self.client_type():
            return ''
        try:
            return self.client.engine()
        except AttributeError:
            return ''

    def is_mobile(self) -> bool:
        if self.device_type() in MOBILE_DEVICE_TYPES:
            return True
        return not self.is_bot() and not self.is_desktop() and not self.is_television()

    def is_desktop(self) -> bool:
        if self.uses_mobile_browser():
            return False
        try:
            return self.os.is_desktop()
        except AttributeError:
            pass
        return False

    def client_name(self) -> str:
        try:
            return self.client.name()
        except AttributeError:
            return ''

    def client_short_name(self) -> str:
        try:
            return self.client.short_name()
        except AttributeError:
            return ''

    def client_version(self) -> str:
        try:
            return self.client.version()
        except AttributeError:
            return ''

    def client_type(self) -> str:
        try:
            return self.client.dtype()
        except AttributeError:
            return ''

    def device_type(self) -> str:
        """
        Get device type, preferably from the Device Parser, but
        calculate from other attributes Device Parser failed.

        Should work, even if skip_device_detection=True
        """
        if self.android_feature_phone():
            return 'smartphone'

        try:
            dt = self.device.dtype()
            if dt:
                return dt
        except AttributeError:
            pass

        aat = self.ambiguous_android_type()
        if aat:
            return aat

        if self.windows_tablet():
            return 'tablet'

        if self.is_television():
            return 'tv'

        if self.is_desktop():
            return 'desktop'

        return ''

    def device_model(self) -> str:
        if not self.device or self.skip_device_detection:
            return ''
        return self.device.model()

    def device_brand_name(self) -> str:
        if self.skip_device_detection:
            return ''
        from .parser import DEVICE_BRANDS
        return DEVICE_BRANDS.get(self.device_brand(), 'UNK')

    def device_brand(self) -> str:
        if self.skip_device_detection:
            return ''
        try:
            brand = self.device.brand_short_name()
        except AttributeError:
            brand = ''

        if brand:
            return brand

        # Assume all devices running iOS / Mac OS are from Apple
        if self.os_short_name() in MAC_iOS:
            return 'AP'

    def os_name(self) -> str:
        try:
            return self.os.name()
        except AttributeError:
            pass
        return ''

    def os_short_name(self) -> str:
        try:
            return self.os.short_name()
        except AttributeError:
            pass
        return ''

    def os_version(self) -> str:
        try:
            return self.os.version()
        except AttributeError:
            pass
        return ''

    def update_device_details(self) -> None:
        """
        Update device details, after all parsing is complete,
        and we have the maximum context available.
        """
        if self.skip_device_detection:
            return

        if 'device' not in self.all_details:
            return

        self.all_details['device'].update({
            'type': self.device_type(),
            'name': self.device_brand_name(),
        })

    def pretty_name(self) -> str:
        return self.all_details['normalized'] or self.user_agent

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
                self.device_brand_name(),
                self.device_model(),
                self.device_type().title(),
            )
        return 'Client: {} Device: {} OS: {}'.format(client, device, os).strip()


class SoftwareDetector(DeviceDetector):

    def __init__(self, user_agent, skip_bot_detection=True, skip_device_detection=True):
        super().__init__(
            user_agent,
            skip_bot_detection=skip_bot_detection,
            skip_device_detection=skip_device_detection,
        )


__all__ = [
    'DeviceDetector',
    'SoftwareDetector',
]
