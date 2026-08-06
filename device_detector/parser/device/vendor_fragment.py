import functools
from typing import Any
from device_detector.yaml_loader import _load_from_yaml
from . import BaseDeviceParser
from ...lazy_regex import RegexLazyIgnore


class VendorFragment(BaseDeviceParser):
    __slots__ = ()

    def _parse(self) -> None:
        user_agent = self.user_agent
        for ua_data in vendor_regex_list():
            for vendor in ua_data['regexes']:
                if matched := vendor.search(user_agent):
                    self.matched_regex = matched
                    self.ua_data = {k: v for k, v in ua_data.items() if k != 'regexes'}
                    self.known = True

                    return


@functools.cache
def vendor_regex_list() -> list[dict[str, Any]]:
    fixture_files = ('upstream/vendorfragments.yml',)

    all_regexes = []
    for fixture in fixture_files:
        regexes = _load_from_yaml(f'regexes/{fixture}')

        for brand, regexes in regexes.items():  # type: ignore[union-attr]
            all_regexes.append({
                'brand': brand,
                'regexes': [RegexLazyIgnore(r) for r in regexes],
            })

    return all_regexes


__all__ = [
    'VendorFragment',
]
