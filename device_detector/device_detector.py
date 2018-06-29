try:
    import regex as re
except ImportError:
    import re

from .parser import (
    OS,

    # Devices
    Bot,
    Device,

    # Clients
    Browser,
    FeedReader,
    Library,
    MediaPlayer,
    MobileApp,
    DesktopApp,
    PIM,
)
from . import DDCache

MAC_iOS = {
    'ATV',
    'IOS',
    'MAC',
}


class DeviceDetector:

    # All registered Client Types
    client_types = []

    CLIENT_PARSERS = (
        FeedReader,
        MobileApp,
        MediaPlayer,
        PIM,
        DesktopApp,
        Browser,
        Library,
    )

    DEVICE_PARSERS = (
        Device,
    )

    def __init__(self, user_agent, skip_bot_detection=False):

        # Holds the useragent that should be parsed
        self.user_agent = user_agent

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
        self.all_details = {}
        self.parsed = False

    @property
    def class_name(self) -> str:
        return self.__class__.__name__

    def get_parse_cache(self):
        if self.user_agent not in DDCache['user_agents']:
            return None
        return DDCache['user_agents'][self.user_agent].get('parsed', None)

    def set_parse_cache(self):
        if self.user_agent not in DDCache['user_agents']:
            DDCache['user_agents'][self.user_agent] = {}
        DDCache['user_agents'][self.user_agent]['parsed'] = self
        return self

    # -----------------------------------------------------------------------------
    # UA parsing methods
    # -----------------------------------------------------------------------------
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

        self.parse_os()
        self.parse_client()
        self.parse_device()

        return self.set_parse_cache()

    def parse_client(self) -> None:
        """
        Parses the UA for client information using the Client parsers
        """
        if self.client:
            return

        for Parser in self.CLIENT_PARSERS:
            parser = Parser(self.user_agent).parse()
            if parser.ua_data:
                self.client = parser
                self.all_details['client'] = parser.ua_data
                return

    def parse_device(self) -> None:
        """
        Parses the UA for Device information using the Device or Bot parsers
        """
        if self.device:
            return

        for Parser in self.DEVICE_PARSERS:
            parser = Parser(self.user_agent).parse()
            if parser.ua_data:
                self.device = parser
                self.all_details['device'] = parser.ua_data
                return

    def parse_bot(self) -> None:
        """
        Parses the UA for bot information using the Bot parser
        """
        if not self.skip_bot_detection and not self.bot:
            self.bot = Bot(self.user_agent).parse()
            self.all_details['bot'] = self.bot.ua_data

    def parse_os(self) -> None:
        """
        Parses the UA for Operating System information using the OS parser
        """
        if not self.os:
            self.os = OS(self.user_agent).parse()
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
        has_touch = re.search('Touch', self.user_agent, re.IGNORECASE) is not None
        return has_touch and self.os_short_name() in ('WRT', 'WIN')

    def is_television(self) -> bool:
        """Devices running Kylo or Espital TV Browsers are assumed to be a TV"""
        if self.client_name() in ('Kylo', 'Espial TV Browser'):
            return True
        regex = 'Kylo|Espial|Opera TV Store|HbbTV'
        return re.search(regex, self.user_agent, re.IGNORECASE) is not None

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
        try:
            return self.client.engine()
        except AttributeError:
            return ''

    def is_mobile(self) -> bool:
        try:
            return self.os.is_mobile()
        except AttributeError:
            return False

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
        if not self.device:
            return ''
        return self.device.model()

    def device_brand_name(self):
        from .parser import DEVICE_BRANDS
        return DEVICE_BRANDS.get(self.device_brand(), 'UNK')

    def device_brand(self) -> str:
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
        if 'device' not in self.all_details:
            return

        self.all_details['device'].update({
            'type': self.device_type(),
            'name': self.device_brand_name(),
        })

    def pretty_print(self) -> str:
        if not self.is_known():
            return self.user_agent
        os = client = device = 'N/A'
        if self.os_name():
            os = '{} {}'.format(self.os_name(), self.os_version())
        if self.client_name():
            client = '{} {} ({})'.format(
                self.client_name(), self.client_version(), self.client_type().title(),
            )
        if self.device_model():
            device = '{} ({})'.format(
                self.device_brand_name(), self.device_model(), self.device_type().title(),
            )
        return 'Client: {} Device: {} OS: {}'.format(client, device, os).strip()


__all__ = (
    'DeviceDetector',
)
