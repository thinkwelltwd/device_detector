from . import GenericClientParser
try:
    import regex as re
except ImportError:
    import re


class NameVersionExtractor(GenericClientParser):
    """
    Generic extractor for user agents that do not have a matching regex and
    have a <name><break><version>, e.g. HotelSearch/187

    Also support user agents that have a
    <name><break><string> format, HotelSearch/ios_5
    """

    name_version = re.compile(
        r'^(?P<name>[\w\d\-_\.\&\'!®\?, ]+)[/ \(]v?(?P<version>[\d\.]+)',
        re.IGNORECASE
    )

    name_slash = re.compile(r'^(?P<name>[\w-]+)/', re.IGNORECASE)

# -------------------------------------------------------------------
    # Regexes that we use to remove unwanted app names
    remove_unwanted_regex = [
        re.compile(r'sm-\w+-android', re.IGNORECASE),
        re.compile(r'^4d531b', re.IGNORECASE),
        re.compile(r'^com\.', re.IGNORECASE),
    ]

# -------------------------------------------------------------------
    # Regexes that we use to parse UA's with a similar structure
    parse_generic_regex = [
        (re.compile(r'([\w ]+)\(unknown version\) cfnetwork$', re.IGNORECASE), 1),
        (re.compile(r'^(fbiossdk)', re.IGNORECASE), 1),
        (re.compile(r'^samsung [\w-]+ (\w+)', re.IGNORECASE), 1),
        (re.compile(r'(pubnub)-csharp', re.IGNORECASE), 1),
        (re.compile(r'(microsoft office)$', re.IGNORECASE), 1),
        (re.compile(r'^(windows assistant)', re.IGNORECASE), 1),
        (re.compile(r'^(liveupdateengine)', re.IGNORECASE), 1),
    ]

# -------------------------------------------------------------------
    app_name = ''
    app_version = ''

    def _parse(self) -> None:

        # prefer name/version format
        match = self.name_version.match(self.user_agent)
        if not match:
            # fall back to name/<worthless-string> format
            match = self.name_slash.match(self.user_agent)

        if not match:
            return

        self.app_name = match.group('name').strip()
        try:
            self.app_version = match.group('version')
        except IndexError:
            self.app_version = ''

        self.clean_name()

        if self.discard_name():
            return

        self.ua_data = {
            'name': self.app_name,
            'version': self.app_version
        }

        self.known = True


__all__ = (
    'NameVersionExtractor',
)
