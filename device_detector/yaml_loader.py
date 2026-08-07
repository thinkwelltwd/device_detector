from collections import defaultdict
import functools
from typing import Any, TypedDict
import ahocorasick_rs
from pathlib import Path
import yaml_rs

import device_detector
from .lazy_regex import RegexLazyIgnore
from .settings import BOUNDED_REGEX, ROOT
from .enums import AppType


class RegexLoader:
    # Paths to yml files of regexes
    fixture_files: tuple[str, ...] = ()

    @property
    def regex_list(self) -> list[dict[str, Any]]:
        return regex_list(self.fixture_files)


class AppNameType(TypedDict):
    name: str
    type: AppType | str


@functools.cache
def app_custom_details() -> dict[str, AppNameType]:
    """
    Load App Details data into dictionary.

    General regex extracts all name/version entries of interest from the UA
    string, and each ParserClass will check to see if any of those names is
    contained in the relevant appdetails.yml file. Much faster than writing
    individual regexes for each app.
    """

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
        all_app_details[dtype] = _load_from_yaml(fixture)

    # convert uaname value to dict key and remove spaces and add that key as well.
    generalized_details: dict = defaultdict(dict)  # type: ignore[type-arg]
    for dtype, entries in all_app_details.items():
        for entry in entries:
            name = entry['name']  # type: ignore[call-overload]
            key = entry['uaname'].lower().replace(' ', '')  # type: ignore[call-overload]
            data = {
                'name': name,
                'type': entry.get('type', dtype),  # type: ignore[union-attr]
            }
            generalized_details[key] = data

            # Match airmail, airmail-android, airmail-iphone
            suffixes = str(entry.get('suffixes', '')).lower().replace(' ', '')  # type: ignore[union-attr]
            for suffix in suffixes.split('|'):
                if suffix:
                    generalized_details[f'{key}{suffix}'] = data

    # Load upstream fixtures last, so that any values that are added
    # upstream later will stomp on local changes.
    for fixture, dtype in (
        ('regexes/upstream/client/hints/browsers.yml', AppType.Browser),
        ('regexes/upstream/client/hints/apps.yml', AppType.MobileApp),
    ):
        for app_id, pretty_name in _load_from_yaml(fixture).items():  # type: ignore[union-attr]
            generalized_details[app_id] = {
                'name': pretty_name,
                'type': dtype,
            }

    return generalized_details


@functools.cache
def regex_list(fixture_files: tuple[str, ...]) -> list[dict[str, Any]]:
    """
    Load regexes from fixture files
    """
    all_regexes = []
    for fixture in fixture_files:
        regexes = _load_from_yaml(f'regexes/{fixture}')
        if isinstance(regexes, list):
            all_regexes.extend(regexes)
            continue
        for entry, regex in regexes.items():
            regexes[entry]['brand'] = entry
            all_regexes.append(regex)

    for regex in all_regexes:
        if 'regex' in regex:
            regex['regex'] = RegexLazyIgnore(BOUNDED_REGEX.format(regex['regex']))
        for model in regex.get('models', []):
            model['regex'] = RegexLazyIgnore(BOUNDED_REGEX.format(model['regex']))
        for version in regex.get('versions', []):
            version['regex'] = RegexLazyIgnore(BOUNDED_REGEX.format(version['regex']))

    return all_regexes


@functools.cache
def normalized_regex_list(fixture: str) -> list[dict[str, Any]]:
    regexes: list[dict[str, Any]] = _load_from_yaml(f'regexes/{fixture}')  # type: ignore[assignment]

    for regex in regexes:
        regex['regex'] = RegexLazyIgnore(regex['regex'])

    return regexes


@functools.lru_cache(256)
def load_ahocorasick_patterns(
    name: str,
    fixture_files: tuple[str, ...],
) -> ahocorasick_rs.AhoCorasick | None:
    """
    Load AhoCorasick words from file, whether manually assigned, or expanded from regexes.
    """
    # Every Parser or Detector class can have a set of words
    # and Word exclusions that are manually defined.
    manual = _load_from_yaml(f'regexes/ahocorasick/classes/{name}.yml') or {}
    all_corasick_words: set[str] = set(manual.get('Words', set())) or set()  # type: ignore[union-attr]

    for fixture in fixture_files:
        if words := set(_load_from_yaml(f'regexes/ahocorasick/{fixture}')):  # noqa
            all_corasick_words.update(words)  # type: ignore[arg-type]

    return ahocorasick_rs.AhoCorasick(all_corasick_words) if all_corasick_words else None


def _load_from_yaml(yml_file: str) -> dict[str, Any] | list[dict[str, Any]] | list[dict[str, Any]]:
    """
    Load YAML from regexes directory, or extract from the egg
    """
    yml_file_path = f'{ROOT}/{yml_file}'
    if Path(yml_file_path).exists():
        with open(yml_file_path, 'r', encoding="utf-8") as yf:
            return yaml_rs.loads(yf.read())

    try:
        yml_file = f'device_detector/{yml_file}'
        return yaml_rs.loads(device_detector.__loader__.get_data(yml_file))  # type: ignore[union-attr]
    except OSError:
        return []
