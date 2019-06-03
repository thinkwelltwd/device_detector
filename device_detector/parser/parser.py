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


class Parser(RegexLoader):

    # Constant used as value for unknown browser / os
    UNKNOWN = 'UNK'

    def __init__(self, ua, ua_hash, ua_spaceless):
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
        self.set_details()
        self.add_to_cache()
        return self.ua_data

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


__all__ = [
    'Parser',
]
