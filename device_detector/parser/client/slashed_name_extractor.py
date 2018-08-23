from . import BaseClientParser
import string
import re


# Manually update this to map app IDs to a user friendly name.
# For example we might want to map 'yp' to 'Yellow Pages'
# Keys should be lowercase
NORMALIZE_ID = {
    'accu-weather': 'AccuWeather',
    'accuweather': 'AccuWeather',
    'test-case': 'Test Case',
    'httpconnection symantec': 'Symantec',
}


# App names that have no value to us so we want to discard them
# Should be lowercase
DISCARD = {
    'product_name',
    'null',
    '4d531b86',
    '4d531b9a',
    'httppostlib',
    'mozilla',
    'sm-g900p-android',
    'sm-j320p-android',
    'mobile_ios'
}


# List of substrings that if found in the app name, we will
# discard the entire app name
# Should be lowercase
UNWANTED_SUBSTRINGS = [
    'ab_1.1.3011',
    'deviceid=',
    'timezone=',
]


# Regexes that we use to remove unwanted app names
REGEX_LIST = [
    r'sm-\w+-android',
    r'^4d531b',
]


class SlashedNameExtractor(BaseClientParser):
    """
    Catch all for user agents that do not have a matching regex and
    use the slash format.

    e.g. <app name>/<version>
    """

    app_name = ''
    app_version = ''

    def _parse(self) -> None:

        try:
            ua_segments = self.user_agent.split('/')
            self.app_name, self.app_version, *_ = ua_segments

        except ValueError:
            return

        self.clean_name()
        self.clean_version()

        if self.discard_name():
            return

        self.app_name = NORMALIZE_ID.get(
            self.app_name.lower(),
            self.app_name
        )

        self.ua_data = {
            'name': self.app_name,
            'version': self.app_version
        }

        self.known = True

    def clean_version(self) -> None:
        """
        Cleanup unwanted data in app version
        """

        self.app_version = self.app_version.split(' ')[0]

    def clean_name(self) -> None:
        """
        Clean unwanted info and characters from app name
        """

        if self.app_name.lower().endswith(' (unknown version) cfnetwork'):
            self.app_name = self.app_name[:-28]

        self.app_name = self.app_name.strip(string.punctuation)

    def discard_name(self) -> bool:
        """
        Determine if app name is of any value to us

        Return True if app should be discarded
        """

        if not self.is_name_length_valid():
            return True

        if self.app_name.lower() in DISCARD:
            return True

        if self.is_substring_unwanted():
            return True

        if self.regex_match():
            return True

        return self.is_name_int()

    def is_name_int(self) -> bool:
        """
        Strip punctuation from app name and return True if
        it can be cast to int
        """

        table = str.maketrans(dict.fromkeys(string.punctuation))
        s = self.app_name.translate(table)

        try:
            int(s)
            return True

        except ValueError:
            return False

    def is_name_length_valid(self) -> None or bool:
        """
        Check if app name portion of UA is between 2 and 25 chars
        """

        if 1 < len(self.app_name) < 26:
            return True

    def is_substring_unwanted(self):
        for substring in UNWANTED_SUBSTRINGS:
            if substring in self.app_name.lower: return True

    def regex_match(self) -> bool or None:
        for regex in REGEX_LIST:
            s = re.search(regex, self.app_name, re.IGNORECASE)

            if s:
                return True

    def dtype(self) -> str:
        return 'generic'


__all__ = (
    'SlashedNameExtractor',
)
