from . import BaseClientParser
import re


class SlashedNameExtractor(BaseClientParser):
    """
    Catch all for user agents that do not have a matching regex and
    use the slash format.

    e.g. <app name>/<version>
    """

# -------------------------------------------------------------------
    # Manually update this to map app IDs to a user friendly name.
    # For example we might want to map 'yp' to 'Yellow Pages'
    # Keys should be lowercase
    normalize_id = {
        'accu-weather': 'AccuWeather',
        'accuweather': 'AccuWeather',
        'test-case': 'Test Case',
        'httpconnection symantec': 'Symantec',
    }

# -------------------------------------------------------------------
    # App names that have no value to us so we want to discard them
    # Should be lowercase
    discard = {
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
        r'sm-\w+-android',
        r'^4d531b',
        r'^com\.'
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

        try:
            ua_segments = self.user_agent.split('/')
            self.app_name, self.app_version, *_ = ua_segments

        except ValueError:
            return

        self.clean_name()
        self.clean_version()

        if self.discard_name():
            return

        self.app_name = self.normalize_id.get(
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
        Extract substring name and remove punctuation from
        app name.
        """

        self.extract_substring_name()

        self.app_name = self.remove_punctuation(self.app_name)

    def extract_substring_name(self) -> None:
        """
        Check if the extracted name uses a known format that we can
        extract helpful info from.  If so, update ua data and mark
        as known.
        """

        for regex in self.parse_generic_regex:
            m = regex[0].match(self.app_name)

            if m:
                self.app_name = m.group(1).strip()
                return

    def dtype(self) -> str:
        return 'generic'


__all__ = (
    'SlashedNameExtractor',
)
