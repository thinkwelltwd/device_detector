import regex
from device_detector.enums import AppType
from device_detector.lazy_regex import RegexLazy
from . import BaseClientParser
from ...parser.key_value_pairs import key_value_pairs
from ...settings import BOUNDED_REGEX
from ..settings import (
    AVAILABLE_BROWSERS,
    AVAILABLE_ENGINES,
    BROWSER_FAMILIES,
    BROWSER_TO_ABBREV,
    FAMILY_FROM_ABBREV,
    CHECK_PAIRS,
    MOBILE_ONLY_BROWSERS,
)

from .extractor_name_version import NameVersionExtractor
from .extractor_whole_name import WholeNameExtractor

DATE_VERSION = RegexLazy(r'^202[0-5]')


class EngineVersion:
    def __init__(self, user_agent: str):
        self.user_agent = user_agent

    def parse(self, engine: str) -> str:
        if not engine:
            return ''

        engine_regex = BOUNDED_REGEX.format(
            r"{engine}\s*\/?\s*((?=\d+\.\d)\d+[.\d]*|\d{{1,7}}(?=(?:\D|$)))".format(engine=engine)
        )
        match = regex.search(engine_regex, self.user_agent, regex.IGNORECASE)
        if match:
            engine_version = self.user_agent[match.start() : match.end()]
            try:
                return engine_version.split('/')[1]
            except IndexError:
                pass

        return ''


class Engine(BaseClientParser):
    __slots__ = ()
    AVAILABLE_ENGINES = AVAILABLE_ENGINES

    fixture_files = [
        'upstream/client/browser_engine.yml',
    ]

    def _parse(self) -> None:
        super()._parse()
        if 'name' in self.ua_data:
            self.ua_data['engine_version'] = EngineVersion(
                self.user_agent,
            ).parse(
                engine=self.ua_data['name'],
            )


class Browser(BaseClientParser):
    __slots__ = ()
    APP_TYPE = AppType.Browser

    fixture_files = [
        'local/client/browsers.yml',
        'upstream/client/browsers.yml',
    ]

    AVAILABLE_ENGINES = AVAILABLE_ENGINES
    AVAILABLE_BROWSERS = AVAILABLE_BROWSERS
    BROWSER_TO_ABBREV = BROWSER_TO_ABBREV
    BROWSER_FAMILIES = BROWSER_FAMILIES
    FAMILY_FROM_ABBREV = FAMILY_FROM_ABBREV
    MOBILE_ONLY_BROWSERS = MOBILE_ONLY_BROWSERS

    def check_all_regexes(self) -> bool | list:
        if check_all := super().check_all_regexes():
            return check_all
        return self.is_ios_fragment()

    def has_interesting_pair(self) -> bool:
        """
        If the UA string has interesting name/version pair(s),
        we don't want to process Browser regexes, but rather
        move on to other parser classes.
        """
        # if the name <= 2 characters, don't consider it interesting
        # if that name is actually interesting, add to relevant
        # appdetails/<file>.yml, so it'll be parsed before now.
        for code, name, version in key_value_pairs(self.user_agent):
            if len(name) > 2 and not name.lower().endswith(('build', 'version')):
                return True
        return False

    def set_details(self) -> None:
        super().set_details()
        self.set_engine()
        self.check_secondary_client_data()
        self.refine_ua_data()

    def refine_ua_data(self) -> None:
        """
        Assemble data from client hints and user agents,
        based on various properties.
        """
        name = self.ua_data.get('name') or ''
        version = self.ua_data.get('version') or ''
        engine = self.ua_data.get('engine') or ''
        engine_version = self.ua_data.get('engine_version') or ''

        # https://bbs.360.cn/thread-16096544-1-1.html
        if version.startswith('114') and engine_version.startswith('15'):
            self.ua_data['version'] = engine_version
            self.ua_data['name'] = '360 Secure Browser'
            self.ua_data['short_name'] = '3B'
            return

        # exclude Blink engine version for Flow browsers
        if engine == 'Blink' and name == 'Flow Browser':
            self.ua_data['engine_version'] = ''
            return

        # the browser simulate ua for Android OS
        if name == 'Every Browser':
            self.ua_data |= {
                'family': 'Chrome',
                'engine': 'Blink',
                'engine_version': '',
            }
            return

        # This browser simulates user-agent of Firefox
        if name == 'TV-Browser Internet' and engine == 'Gecko':
            self.ua_data |= {
                'family': 'Chrome',
                'engine': 'Blink',
                'engine_version': '',
            }
            return

        if engine == 'Blink' and name in ('Yaani Browser', 'Wolvic'):
            self.ua_data['family'] = 'Chrome'
            return

        if engine == 'Gecko' and name in ('Yaani Browser', 'Wolvic'):
            self.ua_data['family'] = 'Firefox'

    def set_data_from_client_hints(self) -> None:
        """
        Save UA data before overriding with Client Hints,
        to restore UA in some cases.
        """
        if not (ch := self.client_hints):
            return

        if not self.ua_data and ch.client_is_browser():
            super().set_data_from_client_hints()
            return

        ch_data = self.ch_client_data
        if ch_data.get('app_id'):
            super().set_data_from_client_hints()
            return

        ch_name = ch_data.get('name', '')
        ch_version = ch_data.get('version', '')
        ua_name = self.ua_data.get('name', '')
        ua_short_name = self.ua_data.get('short_name', '')

        if ua_name in ('Chrome', 'Chrome Mobile') and ch_name == 'Chrome Webview':
            super().set_data_from_client_hints()
            return

        if ch_name == 'DuckDuckGo Privacy Browser':
            super().set_data_from_client_hints()
            self.ua_data['version'] = ''
            self.ua_data['engine_version'] = ch_version
            return

        # If client hints report Chromium, but user agent
        # detects a Chromium based browser, don't add the
        # data from the client hints
        if ua_name and ch_name in ('Chromium', 'Chrome Webview'):
            # If the version reported from the client hints is YYYY or YYYY.MM,
            # then it is the Iridium browser, based on Chromium
            if DATE_VERSION.search(ch_version):
                self.ua_data['name'] = 'Iridium'
                self.ua_data['short_name'] = 'I1'
                return

            if ua_short_name not in ('CR', 'CV', 'AN', 'CM'):
                self.ua_data['name'] = ua_name
                self.ua_data['version'] = self.ua_data.get('version', '')
                self.ua_data['short_name'] = ua_short_name
                return

        super().set_data_from_client_hints()

        # Fix mobile browser names e.g. Chrome => Chrome Mobile
        if f'{ch_name} Mobile' == ua_name:
            self.ua_data['name'] = ua_name
            self.ua_data['short_name'] = ua_short_name

    def short_name(self) -> str:
        return self.ua_data.get('short_name', None)

    def set_engine(self) -> None:
        """
        Extract name from dict:
        {
            'name': 'Chrome',
            'version': '123.0.6312.40',
            'engine': {'default': 'WebKit', 'versions': {28: 'Blink'}},
        }
        """
        if not self.ua_data.get('engine', ''):
            return

        browser = self.ua_data.get('name', '')
        abbreviation = self.BROWSER_TO_ABBREV.get(browser.lower(), browser)
        self.ua_data |= {
            'short_name': abbreviation,
            'family': self.FAMILY_FROM_ABBREV.get(abbreviation, browser),
        }

        if 'engine' not in self.ua_data:
            engine = Engine(self.user_agent, self.ua_spaceless, self.client_hints).parse().ua_data
            self.ua_data['engine'] = engine
            return

        client_version = self.ch_client_data.get('version', '') or self.ua_data.get('version', '')
        engine = self.ua_data.get('engine') or {}
        for _, name in engine.get('versions', {}).items():
            self.ua_data |= {
                'engine': name,
                'engine_version': client_version,
            }

    def is_mobile_only(self) -> bool:
        return self.short_name() in self.MOBILE_ONLY_BROWSERS

    def check_secondary_client_data(self) -> None:
        """
        If the UA string matched is a browser that often
        contains more specific app information, check to
        see if name_version_pairs has data of interest.
        """
        # Call these extractors here, since this regex matching as
        # browser means no further Client Parsers would be run.
        if self.ua_data.get('name', '') in CHECK_PAIRS:
            if self.has_interesting_pair():
                self.get_secondary_client_data(extractor=NameVersionExtractor)
            else:
                self.get_secondary_client_data(extractor=WholeNameExtractor)

    def get_secondary_client_data(
        self,
        extractor: type[NameVersionExtractor] | type[WholeNameExtractor],
    ) -> None:
        """
        Update secondary_client dict with any data from specified extractor
        """
        parsed = extractor(
            ua=self.user_agent,
            ua_spaceless=self.ua_spaceless,
            client_hints=self.client_hints,
        ).parse()

        if parsed.ua_data:
            self.secondary_client = parsed.ua_data
            self.ua_data['secondary_client'] = parsed.ua_data
        else:
            self.secondary_client = {}


__all__ = (
    'Browser',
    'Engine',
    'EngineVersion',
)
