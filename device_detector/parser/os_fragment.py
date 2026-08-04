import functools
from typing import Any
from device_detector.yaml_loader import _load_from_yaml
from . import BaseDeviceParser
from ..lazy_regex import RegexLazyIgnore


class OSFragment(BaseDeviceParser):
    def _parse(self) -> None:
        for ua_data in os_regex_list():
            for regex in ua_data['regexes']:
                matched = regex.search(self.user_agent)

                if matched:
                    self.matched_regex = matched
                    self.ua_data['name'] = ua_data['name']
                    self.known = True

                    return


@functools.cache
def os_regex_list() -> list[dict[str, Any]]:
    fixture_files = ('local/osfragments.yml',)

    all_regexes = []
    for fixture in fixture_files:
        regexes = _load_from_yaml(f'regexes/{fixture}')

        # load and compile regexes. Not using boundaries.
        for os, regexes in regexes.items():  # type: ignore[union-attr]
            all_regexes.append({
                'name': os,
                'regexes': [RegexLazyIgnore(reg) for reg in regexes],
            })

    return all_regexes


__all__ = [
    'OSFragment',
]
