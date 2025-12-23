import string

from ...enums import AppType
from ...lazy_regex import RegexLazyIgnore
from ..parser import Parser
from ...utils import calculate_dtype

keep = frozenset(['!', '@', '+'])
table = str.maketrans(dict.fromkeys(''.join(c for c in string.punctuation if c not in keep)))

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
    # If this client parser class matches, also
    # check the UA string for an application id.
    # Disable that check if the application id
    # is used for many different apps and would
    # result in a loss of precise app names.
    CHECK_APP_ID = True
    __slots__ = ()
    APP_TYPE = AppType.Unknown

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
        self.set_data_from_client_hints()

        super().set_details()
        if self.known and not self.ua_data.get('type'):
            self.ua_data['type'] = self.dtype()

        if custom_app_details := self.appdetails_data.get(self.name().lower()):
            self.ua_data |= custom_app_details


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


__all__ = (
    'BaseClientParser',
    'GenericClientParser',
)
