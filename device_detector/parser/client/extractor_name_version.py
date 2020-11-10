from . import GenericClientParser
from ..settings import METADATA_NAMES


class NameVersionExtractor(GenericClientParser):
    """
    Generic extractor for user agents that do not have a matching regex and
    have a <name><break><version>, e.g. HotelSearch/187

    Also support user agents that have a
    <name><break><string> format, HotelSearch/ios_5

    Checks all name/version pairs, preferring any name that the UA string
    starts with. If that beginning of the UA string isn't interesting,
    prefer the longest name in the name/value pair list.
    """

    # -------------------------------------------------------------------
    app_name = ''
    app_version = ''

    def parse_name_version_pairs(self):
        """
        Check all name/version pairs for most interesting values
        """
        name_version_pairs = self.name_version_pairs()

        for code, name, version in name_version_pairs:

            # Only extract interesting pairs!
            if name.isdigit() \
                    or len(name) == 1 \
                    or code in METADATA_NAMES \
                    or code.endswith(('version', 'build')):
                continue

            # prefer the name that the UA starts with
            if self.user_agent.startswith(name):
                self.app_name = name
                self.app_version = version
                return

            # consider longest name the most interesting
            if len(name) > len(self.app_name):
                self.app_name = name
                self.app_version = version

    def version_contains_numbers(self):
        """
        Version contains no numeric characters
        """
        if not self.app_version:
            return False

        for char in self.app_version:
            if char.isnumeric():
                return True

        return False

    def _parse(self) -> None:

        self.parse_name_version_pairs()

        if not self.app_name:
            return

        if self.discard_name():
            return

        self.ua_data = {
            'name': self.app_name,
            'version': self.app_version if self.version_contains_numbers() else '',
        }

        self.known = True


__all__ = [
    'NameVersionExtractor',
]
