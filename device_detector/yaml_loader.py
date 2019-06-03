try:
    import regex as re
except (ImportError, ModuleNotFoundError):
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

    # Paths to App Details files where lists of name/version patterns are
    # loaded into dicts for fast lookup. Much faster than using regexes.
    appdetails_files = []

    # Constant used as value for unknown browser / os
    UNKNOWN = 'UNK'

    @staticmethod
    def load_from_yaml(yfile):
        """
        Load yaml from regexes directory, or extract from the egg
        """
        if Path('{}/{}'.format(ROOT, yfile)).exists():
            with open('{}/{}'.format(ROOT, yfile), 'r') as yf:
                return yaml.load(yf, SafeLoader)

        try:
            yfile = 'device_detector/{}'.format(yfile)
            return yaml.load(device_detector.__loader__.get_data(yfile), SafeLoader)
        except OSError:
            print('{} does not exist'.format(yfile))
            return []

    def load_app_id_sets(self, name) -> set:
        """
        Load App IDs by key name into python set
        """
        cache_key = 'appids_%s' % name
        app_ids = DDCache[cache_key]
        if app_ids:
            return app_ids

        app_ids = set(self.load_from_yaml('appids/%s.yml' % name))
        DDCache['appids_%s' % name] = app_ids
        return app_ids

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
            regexes.extend(self.yaml_to_list('regexes/{}'.format(fixture)))

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
            regexes.extend(self.yaml_to_list('regexes/{}'.format(fixture)))

        for regex in regexes:
            regex['regex'] = re.compile(regex['regex'], re.IGNORECASE)

        DDCache['normalize_regexes'] = regexes

        return regexes

    @property
    def appdetails_data(self) -> dict:
        """
        Load App Details data into dictionary.

        General regex extracts all name/version entries of interest from the UA
        string, and each ParserClass will check to see if any of those names is
        contained in the relevant appdetails.yml file. Much faster than writing
        individual regexes for each app.
        """
        appdetails = DDCache['appdetails'].get(self.dtype(), {})
        if appdetails:
            return appdetails

        all_app_details = []
        for fixture in self.appdetails_files:
            all_app_details.extend(self.yaml_to_list('{}'.format(fixture)))

        # convert uaname value to dict key and remove spaces
        # and add that key as well.
        generalized_details = {}
        for entry in all_app_details:
            name = entry['name']
            key = entry['uaname'].lower().replace(' ', '')
            data = {
                'name': name,
                'type': entry.get('type', ''),
            }
            generalized_details[key] = data

            # Match airmail, airmail-android, airmail-iphone
            suffixes = str(entry.get('suffixes', '')).lower().replace(' ', '')
            for suffix in suffixes.split('|'):
                key_suffix = '%s%s' % (key, suffix)
                generalized_details[key_suffix] = data

        DDCache['appdetails'][self.dtype()] = generalized_details

        return generalized_details
