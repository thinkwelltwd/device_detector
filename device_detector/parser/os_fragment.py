from . import BaseDeviceParser
from ..lazy_regex import RegexLazyIgnore


class OSFragment(BaseDeviceParser):
    fixture_files = [
        'local/osfragments.yml',
    ]

    def yaml_to_list(self, yfile: str) -> list:
        """
        List of dicts like so:

        {'name': 'iOS', 'regexes': ['iPhone', 'iPad']}
        """
        new_regexes = self.load_from_yaml(yfile)
        reg_list = []

        # load and compile regexes. Not using boundaries.
        for os, regexes in new_regexes.items():  # type: ignore[union-attr]
            reg_list.append({
                'name': os,
                'regexes': [RegexLazyIgnore(reg) for reg in regexes],
            })

        return reg_list

    def _parse(self) -> None:
        for ua_data in self.regex_list:
            for regex in ua_data['regexes']:
                matched = regex.search(self.user_agent)

                if matched:
                    self.matched_regex = matched
                    self.ua_data['name'] = ua_data['name']
                    self.known = True

                    return


__all__ = [
    'OSFragment',
]
