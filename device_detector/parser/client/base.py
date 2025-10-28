import string

from ...enums import AppType
from ...lazy_regex import RegexLazyIgnore
from ..parser import Parser
from ...parser.key_value_pairs import key_value_pairs
from ...settings import DDCache
from ...utils import calculate_dtype

keep = frozenset(['!', '@', '+'])
table = str.maketrans(dict.fromkeys(''.join(c for c in string.punctuation if c not in keep)))

FIRST_ALPHANUMERIC_WORD = RegexLazyIgnore(r'^([a-z0-9]+)')

# fmt: off
UNWANTED_UA_STRINGS = [
    # 13F7BD1A-F6FF-411E-BF5E
    # 4UWWU-WBDXC-VYFN3-QDJMH
    RegexLazyIgnore(r"([\d\w]{4,10}-){3}[\d\w]{4,10}$"),

    # long gibberish string, starting with integer and containing no punctuation
    RegexLazyIgnore(r'^\d[\d\w]{20,40}$'),
]

UNWANTED_APP_NAMES = [
    RegexLazyIgnore(r'sm-\w+-android'),
    RegexLazyIgnore(r'^4d531b'),

    # App IDs will be parsed with ApplicationID extractor
    RegexLazyIgnore(r'^com\.'),
]
# fmt: on


class BaseClientParser(Parser):
    __slots__ = ()
    APP_TYPE = AppType.Unknown

    def name_version_pairs(self) -> list:
        """
        Extract key/value pairs from User Agent String, based on various patterns of:
        <name><sep><version>
        """
        cached = DDCache['user_agents'][self.ua_hash].get('name_version_pairs', None)
        if cached is not None:
            return cached

        name_version_pairs = key_value_pairs(ua=self.user_agent)

        DDCache['user_agents'][self.ua_hash]['name_version_pairs'] = name_version_pairs
        return name_version_pairs

    def matches_manual_appdetails(self) -> bool:
        """
        Check the name_version_pairs data if regexes didn't match anything.

        Each subclass may have `appdetails/<name>.yml` file(s) defined
        containing manually specified details for the regex.
        """
        name = self.ua_data.get('name')
        if name and name != '$1':
            return False

        app_details = self.appdetails_data.get(self.APP_TYPE)
        if not app_details:
            return False

        name_version_pairs = self.name_version_pairs()

        for code, name, version in name_version_pairs:
            if code in app_details:
                self.known = True
                self.ua_data = {
                    'name': app_details[code]['name'],
                    'version': version,
                    'type': app_details[code].get('type', ''),
                }
                return True

        # check if whole UA string found in app details
        match = app_details.get(self.ua_spaceless, {})

        # Check if first alphanumeric word found in app details.
        if not match:
            try:
                first_word = FIRST_ALPHANUMERIC_WORD.search(self.ua_spaceless).group()
                match = app_details.get(first_word, {})
            except AttributeError:
                pass

        if match:
            match['version'] = None
            self.ua_data = match
            return True

        return False

    def set_data_from_client_hints(self) -> None:
        """
        Prefer client hints over user agent data generally.
        Override on subclasses to customize order
        """
        if self.ua_data and self.ch_client_data:
            self.ua_data |= self.ch_client_data

    def dtype(self) -> AppType | str:
        return self.APP_TYPE

    def set_details(self) -> None:
        """
        Set app data from UA or Client Hints.
        """
        self.matches_manual_appdetails()
        self.set_data_from_client_hints()

        super().set_details()
        if self.known and not self.ua_data.get('type'):
            self.ua_data['type'] = self.dtype()


class GenericClientParser(BaseClientParser):
    APP_TYPE = AppType.Generic

    # -------------------------------------------------------------------
    # App names that have no value to us so we want to discard them
    # Should be lowercase
    discard = {
        'productname',
        'null',
        'httppostlib',
        'mozilla',
        'mobileios',
    }

    # -------------------------------------------------------------------
    # List of substrings that if found in the app name, we will
    # discard the entire app name
    # Should be lowercase
    unwanted_substrings = [
        'ab_1.1.3011',
        'deviceid=',
        'timezone=',
    ]

    def discard_name(self) -> bool:
        """
        Determine if app name is of any value to us

        Return True if app should be discarded
        """
        if self.unwanted_regex_match():
            return True

        if not self.is_name_length_valid():
            return True

        if self.app_name_no_punc().lower() in self.discard:
            return True

        if self.is_substring_unwanted():
            return True

        if self.unwanted_regex_name_match():
            return True

        return self.is_name_mostly_numeric()

    def is_name_length_valid(self) -> bool:
        """
        Check if app name portion of UA is between 1 and 45 chars
        """
        return 1 < len(self.app_name) <= 45

    def is_substring_unwanted(self) -> bool:
        for substring in self.unwanted_substrings:
            if substring in self.app_name.lower():
                return True

        return False

    def unwanted_regex_match(self) -> bool:
        for regex in UNWANTED_UA_STRINGS:
            if regex.search(self.user_agent):
                return True

        return False

    def unwanted_regex_name_match(self) -> bool:
        for regex in UNWANTED_APP_NAMES:
            if regex.search(self.app_name):
                return True

        return False

    def is_name_mostly_numeric(self) -> bool:
        """
        Strip punctuation from app name and return True if
        alphabetic characters are less than 50% of the string
        """
        app_no_punc = self.app_name_no_punc()
        if not app_no_punc:
            return True

        try:
            int(app_no_punc)
            return True
        except ValueError:
            pass

        alphabetic_chars = 0
        for char in app_no_punc:
            if not char.isnumeric():
                alphabetic_chars += 1

        threshold = 0.25 if len(self.app_name) < 10 else 0.5

        return alphabetic_chars / len(app_no_punc) < threshold

    def app_name_no_punc(self) -> str:
        """
        Remove punctuation from the given string and return
        the new string
        """
        if self.app_name_no_punctuation:
            return self.app_name_no_punctuation

        self.app_name_no_punctuation = self.app_name.translate(table)

        return self.app_name_no_punctuation

    def dtype(self) -> AppType | str:
        return calculate_dtype(app_name=self.app_name) or self.APP_TYPE

    def check_manual_appdetails(self) -> None:
        """
        Check to see if this app matches any values defined the appdetails yml files,
        and if so, apply the name and app type.
        """
        if not self.app_name:
            return

        app_details = self.appdetails_data
        if not app_details:
            return

        code = self.app_name.lower().replace('_', '').replace(' ', '')

        for dtype, apps in app_details.items():
            if code not in apps:
                continue

            app_details_data = apps.get(code)
            self.app_name = app_details_data['name']
            self.calculated_dtype = app_details_data.get('type') or self.APP_TYPE
            return


__all__ = (
    'BaseClientParser',
    'GenericClientParser',
)
