from collections import defaultdict
import yaml
try:
    from yaml import CSafeLoader as SafeLoader
except ImportError:
    from yaml import SafeLoader
from pathlib import Path

import device_detector
from .lazy_regex import RegexLazyIgnore
from .settings import BOUNDED_REGEX, DDCache, ROOT


class RegexLoader:

    # Paths to yml files of regexes
    fixture_files = []

    # Constant used as value for unknown browser / os
    UNKNOWN = 'UNK'

    def __init__(self, version_truncation=1):
        self.VERSION_TRUNCATION = version_truncation

    @staticmethod
    def load_from_yaml(yfile):
        """
        Load yaml from regexes directory, or extract from the egg
        """
        if Path('{}/{}'.format(ROOT, yfile)).exists():
            with open('{}/{}'.format(ROOT, yfile), 'r', encoding="utf-8") as yf:
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
                regex['regex'] = RegexLazyIgnore(BOUNDED_REGEX.format(regex['regex']))
            for model in regex.get('models', []):
                model['regex'] = RegexLazyIgnore(BOUNDED_REGEX.format(model['regex']))
            for version in regex.get('versions', []):
                version['regex'] = RegexLazyIgnore(BOUNDED_REGEX.format(version['regex']))

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
            regex['regex'] = RegexLazyIgnore(regex['regex'])

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
        appdetails = DDCache['appdetails']
        if appdetails:
            return appdetails

        all_app_details = {}
        for fixture in (
                'appdetails/desktop_app.yml',
                'appdetails/game.yml',
                'appdetails/library.yml',
                'appdetails/mediaplayer.yml',
                'appdetails/messaging.yml',
                'appdetails/mobile_app.yml',
                'appdetails/p2p.yml',
                'appdetails/pim.yml',
                'appdetails/vpnproxy.yml',
        ):
            # Fixture file names are significant!
            # Normalized file name must be a "dtype" of an Client Parser class
            name = fixture.split('/')[-1]
            default_type = name[:-4].replace('_', ' ')
            all_app_details[default_type] = self.yaml_to_list('{}'.format(fixture))

        # convert uaname value to dict key and remove spaces and add that key as well.
        generalized_details = defaultdict(dict)
        for dtype, entries in all_app_details.items():
            for entry in entries:
                name = entry['name']
                key = entry['uaname'].lower().replace(' ', '')
                data = {
                    'name': name,
                    'type': entry.get('type', dtype),
                }
                generalized_details[dtype][key] = data

                # Match airmail, airmail-android, airmail-iphone
                suffixes = str(entry.get('suffixes', '')).lower().replace(' ', '')
                for suffix in suffixes.split('|'):
                    if not suffix:
                        continue
                    generalized_details[dtype]['%s%s' % (key, suffix)] = data
                    generalized_details[dtype]['%s %s' % (key, suffix)] = data

        DDCache['appdetails'] = generalized_details

        return generalized_details

    def clear_cache(self):
        """
        Helper method to clear cache on tests.
        """
        DDCache.clear()
        return self
