try:
    import regex as re
except (ImportError, ModuleNotFoundError):
    import re
from . import BaseClientParser
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


class EngineVersion:

    def __init__(self, user_agent):
        self.user_agent = user_agent

    def parse(self, engine) -> str:
        if not engine:
            return ''

        regex = r"{engine}\s*\/?\s*((?=\d+\.\d)\d+[.\d]*|\d{{1,7}}(?=(?:\D|$)))".format(
            engine=engine
        )
        regex = BOUNDED_REGEX.format(regex)
        match = re.search(regex, self.user_agent, re.IGNORECASE)
        if match:
            engine_version = self.user_agent[match.start():match.end()]
            try:
                return engine_version.split('/')[1]
            except IndexError:
                pass

        return ''


class Engine(BaseClientParser):

    AVAILABLE_ENGINES = AVAILABLE_ENGINES

    fixture_files = [
        'upstream/client/browser_engine.yml',
    ]

    def _parse(self):
        super()._parse()
        if 'name' in self.ua_data:
            self.ua_data['engine_version'] = EngineVersion(
                self.user_agent,
            ).parse(
                engine=self.ua_data['name'],
            )


class Browser(BaseClientParser):

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

    def has_interesting_pair(self):
        """
        If the UA string has interesting name/version pair(s),
        we don't want to process Browser regexes, but rather
        move on to other parser classes.
        """
        # if the name <= 2 characters, don't consider it interesting
        # if that name is actually interesting, add to relevant
        # appdetails/<file>.yml, so it'll be parsed before now.
        for code, name, version in self.name_version_pairs():
            if len(name) > 2 and not name.lower().endswith(('build', 'version')):
                return True
        return False

    def set_details(self):
        super().set_details()
        if self.ua_data:
            browser = self.ua_data.get('name', '')
            abbrevation = self.BROWSER_TO_ABBREV.get(browser.lower(), browser)
            self.ua_data.update({
                'short_name': abbrevation,
                'family': self.FAMILY_FROM_ABBREV.get(abbrevation, browser),
            })

            if 'engine' not in self.ua_data:
                self.ua_data['engine'] = Engine(
                    self.user_agent,
                    self.ua_hash,
                    self.ua_spaceless,
                    self.VERSION_TRUNCATION,
                ).parse().ua_data

    def short_name(self) -> str:
        return self.ua_data.get('short_name', None)

    def engine(self):
        if not self.ua_data.get('engine', ''):
            return ''
        if 'default' in self.ua_data['engine']:
            return self.ua_data['engine']['default']
        return self.ua_data['engine']['name']

    def is_mobile_only(self):
        return self.short_name() in self.MOBILE_ONLY_BROWSERS

    def _parse(self) -> None:
        super()._parse()
        self.check_secondary_client_data()

    def check_secondary_client_data(self):
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

    def get_secondary_client_data(self, extractor):
        """
        Update secondary_client dict with any data from specified extractor
        """
        parsed = extractor(
            ua=self.user_agent,
            ua_hash=self.ua_hash,
            ua_spaceless=self.ua_spaceless,
            version_truncation=self.VERSION_TRUNCATION,
        ).parse()

        if parsed.ua_data:
            self.secondary_client = parsed.ua_data
            self.ua_data['secondary_client'] = parsed.ua_data


__all__ = (
    'Browser',
    'Engine',
    'EngineVersion',
)
