try:
    import regex as re
except ImportError:
    import re
import yaml
try:
    from yaml import CSafeLoader as SafeLoader
except ImportError:
    from yaml import SafeLoader

import device_detector
from functools import lru_cache
from pathlib import Path
from ..settings import (
    BOUNDED_REGEX,
    DDCache,
    ROOT,
)
from .extractors import (
    NameExtractor,
    ModelExtractor,
    VersionExtractor,
)

@lru_cache(None)
def compiled_regex(regex):
    return re.compile(BOUNDED_REGEX.format(regex), re.IGNORECASE)


class Parser:

    # Paths to yml files of regexes
    fixture_files = []

    # Constant used as value for unknown browser / os
    UNKNOWN = 'UNK'

    def __init__(self, ua):
        self.user_agent = ua
        self.ua_data = {}
        self.matched_regex = None
        self.known = False
        if self.user_agent not in DDCache['user_agents']:
            DDCache['user_agents'][self.user_agent] = {}

    @property
    def cache_name(self) -> str:
        """Class name, used for cache key"""
        return self.__class__.__name__

    def dtype(self) -> str:
        """
        For adding 'type' key to ua_data
        """
        return self.cache_name.lower()

    def get_from_cache(self) -> dict:
        return DDCache['user_agents'][self.user_agent].get(self.cache_name, None)

    def add_to_cache(self) -> dict:
        DDCache['user_agents'][self.user_agent][self.cache_name] = self.ua_data
        return self.ua_data

    @staticmethod
    def load_from_yaml(yfile):
        """
        Load yaml from regexes directory, or extract from the egg
        """
        yfilepath = 'regexes/{}'.format(yfile)
        if Path('{}/{}'.format(ROOT, yfilepath)).exists():
            with open('{}/{}'.format(ROOT, yfilepath), 'r') as yf:
                return yaml.load(yf, SafeLoader)

        try:
            yfilepath = 'device_detector/regexes/{}'.format(yfile)
            return yaml.load(device_detector.__loader__.get_data(yfilepath), SafeLoader)
        except OSError:
            print('{} does not exist'.format(yfile))
            return []

    def yaml_to_list(self, yfile) -> list:
        """
        Override method on subclasses if yaml format varies.

        Load yaml file to list of dicts
        """
        regexes = self.load_from_yaml(yfile)
        if isinstance(regexes, list):
            return regexes

        reg_list = []
        for entry in regexes:
            regexes[entry]['name'] = entry
            reg_list.append(regexes[entry])

        return reg_list

    @property
    def regex_list(self) -> list:
        regexes = DDCache['regexes'].get(self.cache_name, [])
        if regexes:
            return regexes

        for fixture in self.fixture_files:
            regexes.extend(self.yaml_to_list(fixture))

        DDCache['regexes'][self.cache_name] = regexes

        return regexes

    def _check_regex(self, regex):
        try:
            cregex = compiled_regex(regex)
            return cregex.search(self.user_agent)
        except Exception as e:
            print('{} fired an error {}'.format(regex, e))
            if re.__name__ == 're':
                print('You are using the builtin "re" library. '
                      'Consider installing the "regex" library instead.')
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

        self.set_details()
        return self

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

        if groups and 'model' in self.ua_data:
            self.ua_data['model'] = ModelExtractor(self.ua_data, groups).extract()

        if groups and 'name' in self.ua_data:
            self.ua_data['name'] = NameExtractor(self.ua_data, groups).extract()

        if groups and 'version' in self.ua_data:
            self.ua_data['version'] = VersionExtractor(self.ua_data, groups).extract()

        # Add type if details were actually found
        if self.ua_data:
            self.ua_data.update({
                'type': self.dtype(),
            })

        self.add_to_cache()

    def name(self) -> str:
        return self.ua_data.get('name', '')

    def short_name(self) -> str:
        return self.ua_data.get('short_name', '')

    def version(self) -> str:
        return self.ua_data.get('version', '')

    def is_known(self) -> bool:
        if self.ua_data:
            return True
        return False


__all__ = (
    'Parser',
)
