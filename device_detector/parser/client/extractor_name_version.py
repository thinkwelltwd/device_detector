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

    __slots__ = ()

    def parse_name_version_pairs(self) -> dict:
        """
        Check all name/version pairs for most interesting values
        """
        name_version_pairs = self.name_version_pairs()
        app_details = self.appdetails_data
        app_type = ''

        for code, name, version in name_version_pairs:
            if app_detail := app_details.get(code):
                self.app_name = app_detail['name']
                self.app_version = version
                app_type = app_detail['type']
                break

            # Only extract interesting pairs!
            if (
                name.isdigit()
                or len(name) == 1
                or code in METADATA_NAMES
                or code.endswith(('version', 'build'))
            ):
                continue

            # prefer the name that the UA starts with
            if self.user_agent.startswith(name):
                self.app_name = name
                self.app_version = version
                break

            # consider the longest name the most interesting
            if len(name) > len(self.app_name):
                self.app_name = name
                self.app_version = version
                break

        return {
            'name': self.app_name,
            'version': self.app_version if self.version_contains_numbers() else '',
            'type': app_type,
        }

    def version_contains_numbers(self) -> bool:
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
        if self.ch_client_data:
            return

        app_data = self.parse_name_version_pairs()

        if not self.app_name:
            return

        if self.discard_name():
            return

        self.ua_data = app_data

        self.known = True


__all__ = [
    'NameVersionExtractor',
]
