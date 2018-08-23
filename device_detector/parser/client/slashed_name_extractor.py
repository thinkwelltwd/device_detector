from . import BaseClientParser
import string


# Manually update this to map app IDs to a user friendly name.
# For example we might want to map 'yp' to 'Yellow Pages'
# Keys should be lowercase
NORMALIZE_ID = {
    'accu-weather': 'AccuWeather',
    'accuweather': 'AccuWeather',
    'test-case': 'Test Case',
}


# App names that have no value to us so we want to discard them
# Should be lowercase
DISCARD = {
    'product_name',
    'null',
    '4d531b86',
    '4d531b9a',
    'httpconnection symantec',
    'httppostlib',
    'mozilla',
    'sm-g900p-android',
    'sm-j320p-android',
    'mobile_ios'
}


# List of substrings that if found in the app name, we will
# discard the entire app name
UNWANTED_SUBSTRINGS = [
    'AB_1.1.3011',
    'DeviceId=',
    'Timezone=',
]


# Characters that we want to strip from app ID
STRIP_CHARS = '(){}$#'


class SlashedNameExtractor(BaseClientParser):
    """
    Catch all for user agents that do not have a matching regex and
    use the slash format.

    e.g. <app name>/<version>
    """

    app_name = ''
    app_version = ''

    def _parse(self):

        try:
            ua_segments = self.user_agent.split('/')
            self.app_name, self.app_version, *_ = ua_segments

        except ValueError:
            return

        # Cleanup unwanted data in app_version
        self.app_version = self.app_version.split(' ')[0]

        self.clean_name()

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

    def clean_name(self):
        """
        Clean unwanted info and characters from app name
        """

        if self.app_name.lower().endswith(' (unknown version) cfnetwork'):
            self.app_name = self.app_name[:-28]

        self.app_name = self.app_name.strip(STRIP_CHARS)

    def discard_name(self):
        """
        Determine if app name is of any value to us

        :return: True if app should be discarded
        """

        if not self.is_name_length_valid():
            return True

        if self.app_name.lower() in DISCARD:
            return True

        for substring in UNWANTED_SUBSTRINGS:
            if substring.lower() in self.app_name.lower: return True

        if self.is_name_int():
            return True

    def is_name_int(self):
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

    def is_name_length_valid(self):
        """
        Check if app name portion of UA is between 2 and 25 chars
        """

        if 1 < len(self.app_name) < 26:
            return True

    def dtype(self):
        return 'generic'


__all__ = (
    'SlashedNameExtractor',
)
