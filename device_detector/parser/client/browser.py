import re
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
JS_BROWSER = re.compile(r'Cypress|PhantomJS', re.IGNORECASE)
CHROME_BLINK = re.compile(r'Chrome/.+ Safari/537\.36', re.IGNORECASE)


class EngineVersion:
    def __init__(self, user_agent: str):
        self.user_agent = user_agent

    def parse(self, engine: str) -> str:
        if not engine:
            return ''

        engine_regex = BOUNDED_REGEX.format(
            r'{engine}\s*\/?\s*((?=\d+\.\d)\d+[.\d]*|\d{{1,7}}(?=(?:\D|$)))'.format(engine=engine)
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

    fixture_files = ('upstream/client/browser_engine.yml',)

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

    fixture_files = (
        'local/client/browsers.yml',
        'upstream/client/browsers.yml',
    )

    AVAILABLE_ENGINES = AVAILABLE_ENGINES
    AVAILABLE_BROWSERS = AVAILABLE_BROWSERS
    BROWSER_TO_ABBREV = BROWSER_TO_ABBREV
    BROWSER_FAMILIES = BROWSER_FAMILIES
    FAMILY_FROM_ABBREV = FAMILY_FROM_ABBREV
    MOBILE_ONLY_BROWSERS = MOBILE_ONLY_BROWSERS

    def check_all_regexes(self) -> bool | list[str]:
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

    def set_data_from_client_hints(self) -> None:
        """
        Save UA data before overriding with Client Hints,
        to restore UA in some cases.
        """
        if not (ch := self.client_hints):
            return

        if not self.ua_data and ch.client_is_browser():
            return super().set_data_from_client_hints()

        ch_data = self.ch_client_data
        ua_data = self.ua_data
        ch_app_type = ch_data.get('type', '')

        ua_name = ua_data.get('name', '')
        ua_short_hame = ua_data.get('short_name') or BROWSER_TO_ABBREV.get(ua_name.lower(), '')
        base_ch_name = self.ch_client_data.get('name', '')

        # Use client hints in favor of user agent data if possible
        if (name := ch_data.get('name')) and (version := ch_data.get('version')):
            short_name = ch_data.get('short_name', '')
            engine = ch_data.get('engine', '')
            engine_version = ch_data.get('engine_version', '')

            # If the version reported from the client hints is YYYY or YYYY.MM (e.g., 2022 or 2022.04),
            # then it is the Iridium browser
            # https://iridiumbrowser.de/news/
            if re.match(r'^202[0-4]', version):
                name = base_ch_name = 'Iridium'
                short_name = 'I1'

            # https://bbs.360.cn/thread-16096544-1-1.html
            if version.startswith('15') and ua_data.get('version', '').startswith('114'):
                name = base_ch_name = '360 Secure Browser'
                short_name = '3B'
                engine = ua_data.get('engine', '')
                engine_version = ua_data.get('engine_version', '')

            # If client hints report the following browsers, we use the version from useragent
            if ua_data.get('version') and short_name in {
                'A0',
                'AL',
                'HP',
                'JR',
                'MU',
                'OM',
                'OP',
                'VR',
            }:
                version = ua_data['version']

            if name == 'Vewd Browser':
                engine = ua_data.get('engine', '')
                engine_version = ua_data.get('engine_version', '')

            # If client hints report Chromium, but user agent detects
            # a Chromium based browser, we favor this instead
            if (
                name in {'Chromium', 'Chrome Webview'}
                and ua_name
                and ua_short_hame not in {'CR', 'CV', 'AN', 'CM'}
            ):
                name = base_ch_name = ua_data.get('name', '')
                short_name = ua_data.get('short_name', '')

            # If user agent detects another browser, but the family
            # matches, we use the detected engine from user agent
            if name != ua_data.get('name') and get_browser_family(name) == get_browser_family(
                ua_data.get('name', '')
            ):
                engine = ua_data.get('engine', '')
                engine_version = ua_data.get('engine_version', '')

            if name == ua_data.get('name'):
                engine = ua_data.get('engine', '')
                engine_version = ua_data.get('engine_version', '')

        else:
            name = ua_data.get('name', '')
            version = ua_data.get('version', '')
            short_name = ua_data.get('short_name', '')
            engine = ua_data.get('engine', '')
            engine_version = ua_data.get('engine_version', '')

        ch_name = ch_data.get('name', '')
        ch_short_name = ch_data.get('short_name', '')
        family = FAMILY_FROM_ABBREV.get(ch_short_name, '')

        # Fix mobile browser names e.g. Chrome => Chrome Mobile
        if f'{ch_name} Mobile' == ua_data.get('name'):
            name = base_ch_name = ua_data.get('name', '')
            short_name = ua_data.get('short_name', '')

        if ch_name and name != base_ch_name:
            name = ch_name
            version = ''
            short_name = ch_short_name

            if CHROME_BLINK.search(self.user_agent):
                engine = 'Blink'
                family = get_browser_family(name) or 'Chrome'

            if short_name is None:
                raise ValueError(
                    f'Detected browser name {name!r} was not found. '
                    f'Tried to parse user agent: {self.user_agent!r}'
                )

        if not name or JS_BROWSER.search(self.user_agent):
            return

        # Browser-specific fixes
        if engine == 'Blink' and name == 'Flow Browser':
            engine_version = ''

        # The browser simulate ua for Android OS
        if name == 'Every Browser':
            family = 'Chrome'
            engine = 'Blink'
            engine_version = ''

        # This browser simulates user-agent of Firefox
        if name == 'TV-Browser Internet' and engine == 'Gecko':
            family = 'Chrome'
            engine = 'Blink'
            engine_version = ''

        if name in {'Yaani Browser', 'Wolvic'}:
            if engine == 'Blink':
                family = 'Chrome'
            elif engine == 'Gecko':
                family = 'Firefox'

        self.ua_data |= {
            'type': ch_app_type if ch_app_type and ch_app_type != 'browser' else 'browser',
            'name': name,
            'short_name': short_name,
            'version': version,
            'engine': engine,
            'engine_version': engine_version,
            'family': family,
        }

    def short_name(self) -> str:
        return self.ua_data.get('short_name') or ''

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
            engine = Engine(self.user_agent, self.client_hints).parse().ua_data
            self.ua_data['engine'] = engine
            return

        client_version = self.ch_client_data.get('version', '') or self.ua_data.get('version', '')
        engine = self.ua_data.get('engine') or {}
        if isinstance(engine, str):
            return

        for name in engine.get('versions', {}).values():
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
            # Prefer client hints since hints tend to be the most precise.
            ch_app_id = self.ch_client_data.get('app_id', '')
            ch_name = self.ch_client_data.get('name', ch_app_id)
            if ch_name:
                self.ua_data['secondary_client'] = {
                    'name': ch_name,
                    'app_id': ch_app_id,
                    'version': self.ch_client_data.get('version', ''),
                }
                return

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
        parsed = extractor(ua=self.user_agent, client_hints=self.client_hints).parse()

        if parsed.ua_data:
            self.secondary_client = parsed.ua_data
            self.ua_data['secondary_client'] = parsed.ua_data
        else:
            self.secondary_client = {}


def get_browser_family(name: str) -> str:
    """
    Get browser family from name
    """
    try:
        return FAMILY_FROM_ABBREV[BROWSER_TO_ABBREV[name.lower()]]
    except KeyError:
        return name


__all__ = (
    'Browser',
    'Engine',
    'EngineVersion',
)
