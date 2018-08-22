from . import BaseClientParser


# Manually update this to map app IDs to a user friendly name.
# For example we might want to map 'yp' to 'Yellow Pages'
# Keys should be lowercase
NORMALIZE_ID = {
    'accu-weather': 'AccuWeather',
    'accuweather': 'AccuWeather',
    'test-case': 'Test Case',
}


# Names that have no value to us so we want to discard them
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
}


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

            self.clean_name()

            self.app_name = NORMALIZE_ID.get(
                self.app_name.lower(),
                self.app_name
            )

            # Cleanup unwanted data in app_version
            self.app_version = self.app_version.split(' ')[0]

        except ValueError:
            return

        if not self.is_name_valid(self.app_name):
            return

        self.ua_data = {
            'name': self.app_name,
            'version': self.app_version
        }

        self.known = True

    def clean_name(self):

        if self.app_name.lower().endswith(' (unknown version) cfnetwork'):
            self.app_name = self.app_name[:-28]

        self.app_name = self.app_name.strip(STRIP_CHARS)

    @staticmethod
    def is_name_valid(app_name):
        """
        Check if app name portion of UA is between 2 and 25 chars
        """

        if 1 < len(app_name) < 26:
            return True

        return False

    def dtype(self):
        return 'generic'


__all__ = (
    'SlashedNameExtractor',
)
