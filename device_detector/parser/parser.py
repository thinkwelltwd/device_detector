try:
    import regex as re
except (ImportError, ModuleNotFoundError):
    import re

from ..settings import (
    DDCache,
)
from .extractors import (
    NameExtractor,
    ModelExtractor,
    VersionExtractor,
)
from ..yaml_loader import RegexLoader


def build_version(version_str: str, truncation=1):
    """
    Extract basic version from strings like 10.0.16299.371

    >>> build_version('10.0.16299.371')
    '10'

    >>> build_version('10')
    '10'
    """
    if truncation == -1:
        return version_str

    retain_segments = truncation + 1

    try:
        segments = version_str.replace('_', '.').split('.')
    except AttributeError:
        return version_str

    if len(segments) == retain_segments:
        return version_str

    return '.'.join(segments[:retain_segments])


class Parser(RegexLoader):

    # Constant used as value for unknown browser / os
    UNKNOWN = 'UNK'
    UNKNOWN_NAME = 'Unknown'

    def __init__(self, ua, ua_hash, ua_spaceless, version_truncation):
        super().__init__(version_truncation)

        self.user_agent = ua
        self.ua_hash = ua_hash
        self.ua_spaceless = ua_spaceless
        self.ua_data = {}
        self.app_name = ''
        self.app_name_no_punctuation = ''
        self.matched_regex = None
        self.app_version = None
        self.known = False
        self.calculated_dtype = ''
        self.secondary_client = {}

    @property
    def cache_name(self) -> str:
        """Class name, used for cache key"""
        return self.__class__.__name__

    def dtype(self) -> str:
        """
        For adding 'type' key to ua_data
        """
        return self.calculated_dtype or self.cache_name.lower()

    def get_from_cache(self) -> dict:
        try:
            return DDCache['user_agents'][self.ua_hash].get(self.cache_name, None)
        except KeyError:
            DDCache['user_agents'][self.ua_hash] = {}
        return {}

    def add_to_cache(self) -> dict:
        DDCache['user_agents'][self.ua_hash][self.cache_name] = self.ua_data
        return self.ua_data

    def _check_regex(self, regex):
        try:
            return regex.search(self.user_agent)
        except Exception as e:
            print('{} fired an error {}'.format(regex, e))
            if re.__name__ == 're':
                print(
                    'You are using the builtin "re" library. '
                    'Consider installing the "regex" library instead.'
                )
            return None

    def _parse(self) -> None:
        """Override on subclasses if custom parsing is required"""
        for ua_data in self.regex_list:
            match = self._check_regex(ua_data['regex'])
            if match:
                self.matched_regex = match
                self.ua_data = ua_data.copy()
                self.known = True
                return

    def parse(self):
        """
        Return parsed details of UA String
        """
        details = self.get_from_cache()
        if details:
            return self

        self._parse()
        self.extract_details()

        return self

    def extract_details(self) -> dict:
        """
        Wrap set_details and call add_to_cache
        """
        self.extract_version()
        self.set_details()
        self.add_to_cache()
        return self.ua_data

    def extract_version(self):
        """
        Extract the version if UA Yaml files specify version regexes.
        See oss.yml for example file structure.
        """
        for version in self.ua_data.pop('versions', []):
            match = self._check_regex(version['regex'])
            if match:
                self.ua_data['version'] = version['version']
                return

    def set_details(self) -> None:
        """
        Override this method on subclasses.

        Update fields with interpolated values from regex data
        """
        if not self.ua_data:
            return
        self.ua_data.pop('regex', False)
        self.ua_data.pop('models', False)
        groups = self.matched_regex and self.matched_regex.groups()

        if groups:
            if 'model' in self.ua_data:
                self.ua_data['model'] = ModelExtractor(self.ua_data, groups).extract()

            if 'name' in self.ua_data:
                self.ua_data['name'] = NameExtractor(self.ua_data, groups).extract()

            if 'version' in self.ua_data:
                self.ua_data['version'] = VersionExtractor(self.ua_data, groups).extract()

        # no version should be considered valid if the name can't be parsed
        if not self.ua_data.get('name') and self.ua_data.get('version'):
            self.ua_data['version'] = ''

        self.ua_data.update({
            'type': self.dtype(),
            'model': (self.ua_data.get('model') or '').replace('_', ' '),
            'version': self.set_version(self.ua_data.get('version', '')),
        })

    def name(self) -> str:
        return self.ua_data.get('name', '')

    def version(self) -> str:
        return self.ua_data.get('version', '')

    def secondary_name(self):
        if self.secondary_client:
            return self.secondary_client['name']
        return ''

    def secondary_version(self):
        if self.secondary_client:
            return self.secondary_client['version']
        return ''

    def secondary_type(self):
        if self.secondary_client:
            return self.secondary_client['type']
        return ''

    def is_known(self) -> bool:
        if self.ua_data:
            return True
        return False

    def set_version(self, version):
        return build_version(version, self.VERSION_TRUNCATION)

    def __str__(self):
        return self.name()

    def __repr__(self):
        return '%s(%s, %s, %s)' % (
            self.__class__.__name__,
            self.user_agent,
            self.ua_hash,
            self.ua_spaceless,
        )


__all__ = [
    'Parser',
]
