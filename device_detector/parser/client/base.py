try:
    import regex as re
except ImportError:
    import re

from ..parser import Parser
import string

keep = {'!', '@', '+'}
table = str.maketrans(dict.fromkeys(''.join(c for c in string.punctuation if c not in keep)))


class BaseClientParser(Parser):

    # Map app names to a user friendly names.
    # For example we might want to map 'yp' to 'Yellow Pages'
    # Keys should be lowercase
    normalized_name = {
        'accu-weather': 'AccuWeather',
        'accuweather': 'AccuWeather',
        'test-case': 'Test Case',
        'httpconnection symantec': 'Symantec',
        'gasbuddy': 'Gas Buddy',
        'icloudservices.exe': 'icloudservices',
        'apsdaemon.exe': 'apsdaemon',
    }

    def normalize_name(self):
        """
        Map app names to a user friendly names.
        For example we might want to map 'yp' to 'Yellow Pages'
        Keys should be lowercase
        """
        name = self.ua_data.get('name', '')
        if not name:
            return
        self.ua_data['name'] = self.normalized_name.get(name.lower(), name)

    def parse(self):
        parsed = super().parse()
        self.normalize_name()
        return parsed

    def dtype(self):
        return self.cache_name.lower()


class GenericClientParser(BaseClientParser):

    # -------------------------------------------------------------------
    # App names that have no value to us so we want to discard them
    # Should be lowercase
    discard = {
        'productname',
        'null',
        'httppostlib',
        'mozilla',
        'mobileios'
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

    # -------------------------------------------------------------------
    # Regexes that we use to remove unwanted app names
    remove_unwanted_regex = [
        re.compile(r'sm-\w+-android', re.IGNORECASE),
        re.compile(r'^4d531b', re.IGNORECASE),

        # App IDs will be parsed with ApplicationID extractor
        re.compile(r'^com\.', re.IGNORECASE),
    ]

    def discard_name(self) -> bool:
        """
        Determine if app name is of any value to us

        Return True if app should be discarded
        """

        if not self.is_name_length_valid():
            return True

        if self.app_name_no_punc().lower() in self.discard:
            return True

        if self.is_substring_unwanted():
            return True

        if self.unwanted_regex_match():
            return True

        return self.is_name_mostly_numeric()

    def is_name_length_valid(self) -> bool:
        """
        Check if app name portion of UA is between 3 and 35 chars
        """
        return 2 < len(self.app_name) <= 35

    def is_substring_unwanted(self):
        for substring in self.unwanted_substrings:
            if substring in self.app_name.lower():
                return True

    def unwanted_regex_match(self) -> bool:
        for regex in self.remove_unwanted_regex:
            if regex.search(self.app_name):
                return True

        return False

    def is_name_mostly_numeric(self) -> bool:
        """
        Strip punctuation from app name and return True if
        alphabetic characters are less than 25% of the string
        """
        app_no_punc = self.app_name_no_punc()

        try:
            int(app_no_punc)
            return True
        except ValueError:
            pass

        alphabetic_chars = 0
        for char in app_no_punc:
            if not char.isnumeric():
                alphabetic_chars += 1

        return alphabetic_chars / len(app_no_punc) < .75

    def app_name_no_punc(self) -> str:
        """
        Remove punctuation from the given string and return
        the new string
        """
        if self.app_name_no_punctuation:
            return self.app_name_no_punctuation

        self.app_name_no_punctuation = self.app_name.translate(table)

        return self.app_name_no_punctuation

    def clean_name(self) -> None:
        """
        Check if the extracted name uses a known format that we can
        extract helpful info from.  If so, update ua data and mark
        as known.
        """

        for regex, group in self.parse_generic_regex:
            m = regex.match(self.app_name)

            if m:
                self.app_name = m.group(group).strip()
                return

    def dtype(self) -> str:
        return 'generic'


__all__ = (
    'BaseClientParser',
    'GenericClientParser',
)
