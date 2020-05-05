from . import BaseDeviceParser
from ...lazy_regex import RegexLazyIgnore


class VendorFragment(BaseDeviceParser):
    fixture_files = [
        'upstream/vendorfragments.yml',
    ]

    def yaml_to_list(self, yfile) -> list:
        """
        List of dicts like so:

        {'name': 'Dell', 'regexes': ['MDDR(JS)?', 'MDDC(JS)?', 'MDDS(JS)?']}
        """
        new_regexes = self.load_from_yaml(yfile)
        reg_list = []

        for brand, regexes in new_regexes.items():
            reg_list.append({
                'name': brand,
                'regexes': [RegexLazyIgnore(r) for r in regexes],
            })

        return reg_list

    def _parse(self) -> None:
        for ua_data in self.regex_list:
            for regex in ua_data['regexes']:
                match = self._check_regex(regex)
                if match:
                    self.matched_regex = match
                    self.ua_data = ua_data.copy()
                    self.known = True

                    name = ua_data['name']
                    self.ua_data['brand'] = self.BRAND_TO_ABBREV.get(name.lower(), name)
                    self.ua_data.pop('regexes', False)

                    return


__all__ = [
    'VendorFragment',
]
