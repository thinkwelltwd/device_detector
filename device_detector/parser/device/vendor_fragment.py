from . import BaseDeviceParser
from ...lazy_regex import RegexLazyIgnore


class VendorFragment(BaseDeviceParser):
    __slots__ = ()
    fixture_files = [
        'upstream/vendorfragments.yml',
    ]

    def yaml_to_list(self, yfile: str) -> list:
        """
        List of dicts like so:

        {'brand': 'Dell', 'regexes': ['MDDR(JS)?', 'MDDC(JS)?', 'MDDS(JS)?']}
        """
        new_regexes = self.load_from_yaml(yfile)
        if isinstance(new_regexes, list):
            return new_regexes

        reg_list = []

        for brand, regexes in new_regexes.items():
            reg_list.append({
                'brand': brand,
                'regexes': [RegexLazyIgnore(r) for r in regexes],
            })

        return reg_list

    def _parse(self) -> None:
        user_agent = self.user_agent
        for ua_data in self.regex_list:
            for vendor in ua_data['regexes']:
                if matched := vendor.search(user_agent):
                    self.matched_regex = matched
                    self.ua_data = {k: v for k, v in ua_data.items() if k != 'regexes'}
                    self.known = True

                    return


__all__ = [
    'VendorFragment',
]
