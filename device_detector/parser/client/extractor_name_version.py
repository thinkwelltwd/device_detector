from . import GenericClientParser
try:
    import regex as re
except (ImportError, ModuleNotFoundError):
    import re


class NameVersionExtractor(GenericClientParser):
    """
    Generic extractor for user agents that do not have a matching regex and
    have a <name><break><version>, e.g. HotelSearch/187

    Also support user agents that have a
    <name><break><string> format, HotelSearch/ios_5
    """
    # Check for name/version matching, in order of desired match
    name_versions = (
        # match where name/version separator is found multiple times,
        # but string ends with version
        # Microsoft URL Control - 6.01.9782
        # openshot-qt-2.4.2
        re.compile(r'(?P<name>.*) ?\- ?(?P<version>[\d\.]+)$', re.IGNORECASE),
        re.compile(r'^(?P<name>[\w\d\-_\.\&\'!®\?, ]+)[/ \(]v?(?P<version>[\d\.]+)', re.IGNORECASE),

        # Name<break>version
        # _iPhone9,1_Chariton_12.0.1
        re.compile(r'.*[\b_](?P<name>\w+)[\b_](?P<version>[\d\.]+)$', re.IGNORECASE),

        # Microsoft.VisualStudio.Help (2.3)
        re.compile(r'(?P<name>.*) [\(\[\{]([\d\.]+)[\)\]\}]$', re.IGNORECASE),

        # name_slash
        re.compile(r'^(?P<name>[\w-]+)/', re.IGNORECASE)
    )

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

        match = None
        for pattern in self.name_versions:
            match = pattern.match(self.user_agent)
            if match:
                break

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
            'version': self.app_version,
        }

        self.known = True


__all__ = [
    'NameVersionExtractor',
]
