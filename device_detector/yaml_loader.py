from collections import defaultdict
from typing import TypedDict
import yaml

try:
    from yaml import CSafeLoader as SafeLoader
except ImportError:
    from yaml import SafeLoader  # type: ignore[assignment]
from pathlib import Path
from typing import Self

import device_detector
from .lazy_regex import RegexLazyIgnore
from .settings import BOUNDED_REGEX, DDCache, ROOT
from .enums import AppType


class RegexLoader:
    # Paths to yml files of regexes
    fixture_files: list[str] | tuple[str, ...] = ()

    # Constant used as value for unknown browser / os
    UNKNOWN = 'UNK'

    @property
    def cache_name(self) -> str:
        """Class name, used for cache key"""
        return self.__class__.__name__

    @staticmethod
    def load_from_yaml(yfile: str) -> dict | list:
        """
        Load yaml from regexes directory, or extract from the egg
        """
        yml_file_path = f'{ROOT}/{yfile}'
        if Path(yml_file_path).exists():
            with open(yml_file_path, 'r', encoding="utf-8") as yf:
                return yaml.load(yf, SafeLoader)

        try:
            yfile = f'device_detector/{yfile}'
            return yaml.load(device_detector.__loader__.get_data(yfile), SafeLoader)  # type: ignore[union-attr]
        except OSError:
            print(f'{yfile} does not exist')
            return []

    def yaml_to_list(self, yfile: str) -> list[dict]:
        """
        Override method on subclasses if yaml format varies.

        Load yaml file to list of dicts
        """
        regexes = self.load_from_yaml(yfile)
        if isinstance(regexes, list):
            return regexes

        reg_list = []
        for entry, regex in regexes.items():
            regexes[entry]['brand'] = entry
            reg_list.append(regex)

        return reg_list

    @property
    def regex_list(self) -> list[dict]:
        if regexes := DDCache['regexes'].get(self.cache_name, []):
            return regexes

        for fixture in self.fixture_files:
            regexes.extend(self.yaml_to_list(f'regexes/{fixture}'))

        for regex in regexes:
            if 'regex' in regex:
                regex['regex'] = RegexLazyIgnore(BOUNDED_REGEX.format(regex['regex']))
            for model in regex.get('models', []):
                model['regex'] = RegexLazyIgnore(BOUNDED_REGEX.format(model['regex']))
            for version in regex.get('versions', []):
                version['regex'] = RegexLazyIgnore(BOUNDED_REGEX.format(version['regex']))

        DDCache['regexes'][self.cache_name] = regexes

        return regexes

    def clear_cache(self) -> Self:
        """
        Helper method to clear cache on tests.
        """
        DDCache.clear()
        return self


class AppNameType(TypedDict):
    name: str
    type: AppType | str


def app_pretty_names_types_data() -> dict[str, AppNameType]:
    """
    Load App Details data into dictionary.

    General regex extracts all name/version entries of interest from the UA
    string, and each ParserClass will check to see if any of those names is
    contained in the relevant appdetails.yml file. Much faster than writing
    individual regexes for each app.
    """
    cache_key = 'app_details'
    if appdetails := DDCache.get(cache_key, {}):
        return appdetails

    regex_loader = RegexLoader()
    all_app_details = {}
    for fixture, dtype in (
        ('appdetails/ai.yml', AppType.ArtificialIntelligence),
        ('appdetails/av.yml', AppType.Antivirus),
        ('appdetails/browser.yml', AppType.Browser),
        ('appdetails/desktop_app.yml', AppType.DesktopApp),
        ('appdetails/game.yml', AppType.Game),
        ('appdetails/library.yml', AppType.Library),
        ('appdetails/mediaplayer.yml', AppType.MediaPlayer),
        ('appdetails/messaging.yml', AppType.Messaging),
        ('appdetails/mobile_app.yml', AppType.MobileApp),
        ('appdetails/navigation.yml', AppType.Navigation),
        ('appdetails/osutility.yml', AppType.OsUtility),
        ('appdetails/p2p.yml', AppType.P2P),
        ('appdetails/pim.yml', AppType.PIM),
        ('appdetails/productivity.yml', AppType.Productivity),
        ('appdetails/vpnproxy.yml', AppType.VpnProxy),
    ):
        all_app_details[dtype] = regex_loader.yaml_to_list(fixture)

    # convert uaname value to dict key and remove spaces and add that key as well.
    generalized_details: dict = defaultdict(dict)
    for dtype, entries in all_app_details.items():
        for entry in entries:
            name = entry['name']
            key = entry['uaname'].lower().replace(' ', '')
            data = {
                'name': name,
                'type': entry.get('type', dtype),
            }
            generalized_details[key] = data

            # Match airmail, airmail-android, airmail-iphone
            suffixes = str(entry.get('suffixes', '')).lower().replace(' ', '')
            for suffix in suffixes.split('|'):
                if suffix:
                    generalized_details[f'{key}{suffix}'] = data

    # Load upstream fixtures last, so that any values that are added
    # upstream later will stomp on local changes.
    for fixture, dtype in (
        ('regexes/upstream/client/hints/browsers.yml', AppType.Browser),
        ('regexes/upstream/client/hints/apps.yml', AppType.MobileApp),
    ):
        for app_id, pretty_name in regex_loader.load_from_yaml(fixture).items():  # type: ignore[union-attr]
            generalized_details[app_id] = {
                'name': pretty_name,
                'type': dtype,
            }

    DDCache[cache_key] = generalized_details

    return generalized_details


def normalized_regex_list(fixture_files: list[str]) -> list:
    cache_key = 'normalize_regexes'
    if regexes := DDCache.get(cache_key, []):
        return regexes

    regex_loader = RegexLoader()
    for fixture in fixture_files:
        regexes.extend(regex_loader.yaml_to_list(f'regexes/{fixture}'))

    for regex in regexes:
        regex['regex'] = RegexLazyIgnore(regex['regex'])

    DDCache[cache_key] = regexes

    return regexes
