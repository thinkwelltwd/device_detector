from typing import Self
from .lazy_regex import RegexLazy
from .enums import DeviceType

from .parser import (
    BaseClientParser,
    BaseDeviceParser,
    ClientHints,
    OS,
    # Device extractors
    Bot,
    Camera,
    CarBrowser,
    Console,
    Device,
    # HbbTv,
    PortableMediaPlayer,
    Notebook,
    # ShellTv,
    MOBILE_DEVICE_TYPES,
    # Clients
    AdobeCC,
    DictUA,
    Browser,
    FeedReader,
    Library,
    MediaPlayer,
    Messaging,
    MobileApp,
    OsUtility,
    Antivirus,
    DesktopApp,
    PIM,
    VPNProxy,
    # Generic name extractors
    ApplicationIDExtractor,
    NameVersionExtractor,
    WholeNameExtractor,
)
from .parser.settings import APPLE_OS_NAMES, TV_CLIENTS
from .settings import BOUNDED_REGEX, DDCache, WORTHLESS_UA_TYPES
from .utils import (
    clean_ua,
    long_ua_no_punctuation,
    mostly_numerals,
    mostly_repeating_characters,
    only_numerals_and_punctuation,
    random_alphanumeric_string,
    uuid_like_name,
    ua_hash,
)
from .yaml_loader import normalized_regex_list

DESKTOP_FRAGMENT = RegexLazy(BOUNDED_REGEX.format(r'(?:Windows (?:NT|IoT)|X11; Linux x86_64)'))


class DeviceDetector:
    fixture_files = [
        'local/device/normalize.yml',
    ]

    CLIENT_PARSERS = (
        AdobeCC,
        DictUA,
        FeedReader,
        Messaging,
        MobileApp,
        MediaPlayer,
        PIM,
        VPNProxy,
        OsUtility,
        Antivirus,
        DesktopApp,
        Browser,
        Library,
        NameVersionExtractor,
        WholeNameExtractor,
    )

    # The order needs to be the same as the order of device
    # parser classes used in the matomo project
    DEVICE_PARSERS = (
        # TV detection not needed currently.
        # PRs passing tests in test_televisions.txt are welcome.
        # HbbTv,
        # ShellTv,
        Console,
        CarBrowser,
        Camera,
        PortableMediaPlayer,
        Notebook,
        Device,
    )

    __slots__ = (
        'client',
        'device',
        'model',
        'user_agent_lower',
        'user_agent',
        'ua_hash',
        '_ua_spaceless',
        'bot',
        'os',
        'skip_bot_detection',
        'skip_device_detection',
        'all_details',
        'parsed',
        'headers',
        'client_hints',
        '_normalized_regex_list',
    )

    def __init__(
        self,
        user_agent: str,
        skip_bot_detection: bool = False,
        skip_device_detection: bool = False,
        headers: dict[str, str] | None = None,
    ):
        """

        Args:
            user_agent: User Agent string to parse
            skip_bot_detection: Skip checking if client is a bot
            skip_device_detection: Skip device brand and model lookup.
            headers: Client Hint headers from the request
        """

        # Holds the useragent that should be parsed
        self.user_agent_lower = user_agent.lower()
        self.user_agent = clean_ua(user_agent, self.user_agent_lower)
        self.ua_hash = ua_hash(self.user_agent, headers)
        self._ua_spaceless = ''
        self.os: OS | None = None
        self.client: BaseClientParser | None = None
        self.device: BaseDeviceParser | None = None
        self.model = ''

        # Holds bot information if parsing the UA results in a bot
        # (All other information attributes will stay empty in that case)
        # If self.discardBotInformation is set to True, this property will be set to
        # True if parsed UA is identified as bot, additional information will be not available
        # If self.skip_bot_detection is set to True, bot detection will not be performed and
        # isBot will always be False
        self.bot: Bot | None = None

        self.skip_bot_detection = skip_bot_detection
        self.skip_device_detection = skip_device_detection
        self.all_details: dict = {'normalized': ''}
        self.parsed = False
        self.headers = headers or {}
        self.client_hints = ClientHints.new(headers) if headers else None
        self._normalized_regex_list = normalized_regex_list(self.fixture_files)

    @property
    def class_name(self) -> str:
        return self.__class__.__name__

    @property
    def ua_spaceless(self) -> str:
        if not self._ua_spaceless:
            self._ua_spaceless = self.user_agent.lower().replace(' ', '')
        return self._ua_spaceless

    def get_parse_cache(self) -> Self | None:
        cached = DDCache['user_agents'].get(self.ua_hash, {}).get('parsed') or None
        if cached:
            self.os = cached.os
            self.client = cached.client
            self.device = cached.device
            self.model = cached.model
            self.all_details = cached.all_details
            self.parsed = cached.parsed
            self.headers = cached.headers
            self.client_hints = cached.client_hints

        return cached

    def set_parse_cache(self) -> Self:
        if self.all_details:
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
        ua = self.user_agent.strip('({})')
        if len(ua) >= 2 and ua[1] == ':':
            ua = self.user_agent[2:]

        return uuid_like_name(ua)

    def is_gibberish(self) -> bool:
        """
        Check for frequently occurring patterns of meaninglessness
        """
        if mostly_repeating_characters(self.user_agent):
            return True

        if random_alphanumeric_string(self.user_agent_lower):
            return True

        return long_ua_no_punctuation(self.user_agent)

    def normalize(self) -> str:
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
            for nr in self._normalized_regex_list:
                regex = nr['regex']
                groups = r'{}'.format(nr['groups'])
                ua = regex.sub(groups, self.user_agent)
                if ua != self.user_agent:
                    self.all_details['normalized'] = ua
                    break
            else:
                self.all_details['normalized'] = ''

        return self.all_details['normalized']

    def is_worthless(self) -> bool:
        """
        Is this UA string of no possible interest?
        """
        self.normalize()
        if self.headers:
            return False
        return self.all_details['normalized'] in WORTHLESS_UA_TYPES

    def parse(self) -> Self:
        if cached := self.get_parse_cache():
            return cached

        if not self.user_agent and not self.headers:
            return self

        if not self.skip_bot_detection:
            self.parse_bot()

        if self.is_worthless():
            return self

        self.parse_os()

        self.parse_client()

        if not self.skip_device_detection:
            self.parse_device()
            # All devices running Coolita OS are assumed to be a tv
            if self.os_name() == 'Coolita OS':
                device_data = {
                    'brand': 'coocaa',
                    'type': DeviceType.TV,
                }
                try:
                    self.all_details['device'] |= device_data
                except KeyError:
                    self.all_details['device'] = device_data

        return self.set_parse_cache()

    def supplement_secondary_client_data(self, app_idx: ApplicationIDExtractor) -> None:
        """
        Add data to secondary_client details
        """
        if not self.client:
            return
        self.client.secondary_client.update(app_idx.details)
        try:
            self.all_details['client']['secondary_client'] |= app_idx.details
        except KeyError:
            self.all_details['client']['secondary_client'] = app_idx.details

    def parse_client(self) -> None:
        """
        Parses the UA for client information using the Client parsers
        """
        if self.client:
            return None

        for Parser in self.CLIENT_PARSERS:
            parser = Parser(
                self.user_agent,
                self.ua_hash,
                self.ua_spaceless,
                self.client_hints,
                os_details=self.all_details.get('os', {}),
            ).parse()

            if parser.ua_data:
                self.client = parser
                self.all_details['client'] = parser.ua_data
                break

        return self.extract_app_id()

    def extract_app_id(self) -> None:
        """
        Extract app_id from UA if not found in client hints.
        """
        if self.client and not self.client.CHECK_APP_ID:
            return

        # If app_id already present, it was extracted from client hints
        if self.all_details.get('client', {}).get('app_id'):
            return

        app_idx = ApplicationIDExtractor(self.user_agent).extract()

        if app_idx.details.get('app_id', ''):
            if not self.all_details.get('client'):
                self.all_details['client'] = app_idx.details
                return

            self.supplement_secondary_client_data(app_idx)

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
                self.client_hints,
                os_details=self.all_details.get('os', {}),
            ).parse()
            if parser.ua_data:
                self.device = parser
                self.all_details['device'] = parser.ua_data
                if (
                    self.all_details['device'] != DeviceType.Desktop
                    and DESKTOP_FRAGMENT.search(self.user_agent) is not None
                ):
                    self.all_details['device']['device'] = DeviceType.Desktop
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
                self.client_hints,
            ).parse()
            self.all_details['bot'] = self.bot.ua_data

    def parse_os(self) -> None:
        """
        Parses the UA for Operating System information using the OS parser
        """
        if not self.os:
            os = OS(
                self.user_agent,
                self.ua_hash,
                self.ua_spaceless,
                self.client_hints,
            ).parse()
            if os:
                self.os = os
                self.all_details['os'] = os.ua_data

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

    def is_television(self) -> bool:
        """
        Detect devices that are likely TVs.

        All devices that contain Andr0id in string are assumed to be a tv
        All devices running Tizen TV or SmartTV are assumed to be a tv
        Devices running known tv clients are assumed to be a TV
        All devices containing TV fragment are assumed to be a tv
        All devices running Coolita OS are assumed to be a tv
        """
        if self.client_name() in TV_CLIENTS:
            return True

        return self.device_type() == DeviceType.TV

    def uses_mobile_browser(self) -> bool:
        if isinstance(self.client, Browser):
            return self.client.is_mobile_only()
        return False

    def engine(self) -> str:
        if 'browser' not in self.client_type():
            return ''
        return self.all_details.get('client', {}).get('engine', '')

    def is_mobile(self) -> bool:
        """
        Returns if the parsed UA is detected as a mobile device
        """
        if self.client_hints and self.client_hints.mobile:
            return self.client_hints.is_mobile()

        if self.device_type() in MOBILE_DEVICE_TYPES:
            return True
        return not self.is_bot() and not self.is_desktop() and not self.is_television()

    def is_desktop(self) -> bool:
        """
        Returns if the parsed UA was identified as desktop device
        Desktop devices are all devices with an unknown type that are running a desktop os
        """
        if self.client_hints and self.client_hints.mobile:
            return self.client_hints.is_desktop()

        if self.uses_mobile_browser():
            return False

        return self.device_type() == DeviceType.Desktop

    def is_feature_phone(self) -> bool:
        """
        Check for various indicators that this is feature phone.
        """
        return self.device_type() == DeviceType.FeaturePhone

    def client_name(self) -> str:
        return self.all_details.get('client', {}).get('name', '')

    def client_version(self) -> str:
        return self.all_details.get('client', {}).get('version', '')

    def client_application_id(self) -> str:
        """
        Return Apple Bundle ID or Android Package ID if present.

        2ndLine/4.8.1 (com.second.phonenumber; build:1.5; iOS 16.7.12) Alamofire/5.4.4
        AcuityApp/5.14.0 (com.acuityscheduling.app.ios; build:1686757700; iPhone; iOS 17.1.1) SquarespaceMobileiOS
        """
        return self.all_details.get('client', {}).get('app_id', '')

    def client_type(self) -> str:
        return self.all_details.get('client', {}).get('type', '')

    def secondary_client_name(self) -> str:
        return self.all_details.get('client', {}).get('secondary_client', {}).get('name', '')

    def secondary_client_version(self) -> str:
        return self.all_details.get('client', {}).get('secondary_client', {}).get('version', '')

    def secondary_client_type(self) -> str:
        return self.all_details.get('client', {}).get('secondary_client', {}).get('type', '')

    def preferred_client_name(self) -> str:
        """
        Android and iOS mobile browsers often contain more interesting
        app information.

        If Secondary app can be extracted, prefer those app details
        as being more specific.
        """
        return self.secondary_client_name() or self.client_name()

    def preferred_client_version(self) -> str:
        return self.secondary_client_version() or self.client_version()

    def preferred_client_type(self) -> str:
        return self.secondary_client_type() or self.client_type()

    def device_type(self) -> DeviceType:
        """
        Get device type, preferably from the Device Parser, but
        calculate from other attributes Device Parser failed.

        Should work, even if skip_device_detection=True
        """
        return self.all_details.get('device', {}).get('type', DeviceType.Unknown)

    def device_model(self) -> str:
        """
        Detect model from UserAgent, and fall back to checking Client Hints
        """
        client_hints_model = self.client_hints and self.client_hints.model or ''
        if self.skip_device_detection:
            return client_hints_model
        return self.all_details.get('device', {}).get('model', client_hints_model)

    def device_brand(self) -> str:
        if self.skip_device_detection:
            return ''

        brand = self.all_details.get('device', {}).get('brand', '')
        if brand:
            return brand

        # Assume all devices running iOS / macOS are from Apple
        if self.os_name() in APPLE_OS_NAMES:
            return 'Apple'

        return ''

    def os_name(self) -> str:
        return self.all_details.get('os', {}).get('name') or ''

    def os_version(self) -> str:
        return self.all_details.get('os', {}).get('version') or ''

    def pretty_name(self) -> str:
        return self.all_details.get('normalized') or self.user_agent or ''

    def pretty_print(self) -> str:
        if not self.is_known():
            return self.user_agent
        os = client = device = 'N/A'
        if self.os_name():
            os = f'{self.os_name()} {self.os_version()}'
        if self.client_name():
            client = f'{self.client_name()} {self.client_version()} ({self.client_type().title()})'
        if self.device_model():
            device = f'{self.device_model()} ({self.device_type().title()})'
        return f'Client: {client} Device: {device} OS: {os}'.strip()

    def __str__(self) -> str:
        return self.user_agent

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.user_agent!r})'


class SoftwareDetector(DeviceDetector):
    def __init__(
        self,
        user_agent: str,
        skip_bot_detection: bool = True,
        skip_device_detection: bool = True,
        headers: dict[str, str] | None = None,
    ):
        super().__init__(
            user_agent,
            skip_bot_detection=skip_bot_detection,
            skip_device_detection=skip_device_detection,
            headers=headers,
        )


__all__ = (
    'DeviceDetector',
    'SoftwareDetector',
)
