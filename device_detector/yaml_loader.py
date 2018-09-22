try:
    import regex as re
except ImportError:
    import re
import yaml
try:
    from yaml import CSafeLoader as SafeLoader
except ImportError:
    from yaml import SafeLoader
from pathlib import Path

import device_detector
from .settings import BOUNDED_REGEX, DDCache, ROOT


class RegexLoader:

    # Paths to yml files of regexes
    fixture_files = []

    # Constant used as value for unknown browser / os
    UNKNOWN = 'UNK'

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

        for regex in regexes:
            if 'regex' in regex:
                regex['regex'] = re.compile(BOUNDED_REGEX.format(regex['regex']), re.IGNORECASE)
            for model in regex.get('models', []):
                model['regex'] = re.compile(BOUNDED_REGEX.format(model['regex']), re.IGNORECASE)

        DDCache['regexes'][self.cache_name] = regexes

        return regexes

    @property
    def normalized_regex_list(self) -> list:
        regexes = DDCache.get('normalize_regexes', [])
        if regexes:
            return regexes

        for fixture in self.fixture_files:
            regexes.extend(self.yaml_to_list(fixture))

        for regex in regexes:
            regex['regex'] = re.compile(regex['regex'], re.IGNORECASE)

        DDCache['normalize_regexes'] = regexes

        return regexes
