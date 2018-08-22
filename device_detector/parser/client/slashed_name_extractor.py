from . import BaseClientParser


# Manually update this to map app IDs to a user friendly name.
# For example we might want to map 'yp' to 'Yellow Pages'
# Keys should be lowercase
NORMALIZE_ID = {
    'accu-weather': 'AccuWeather',
    'accuweather': 'AccuWeather',
    'test-case': 'Test Case',
}


class SlashedNameExtractor(BaseClientParser):
    """
    Catch all for user agents that do not have a matching regex and
    use the slash format.

    e.g. <app name>/<version>
    """

    def _parse(self):

        try:
            ua_segments = self.user_agent.split('/')
            app_name, app_version, *_ = ua_segments
            app_name = NORMALIZE_ID.get(app_name.lower(), app_name)

            # Cleanup unwanted data in app_version
            app_version = app_version.split(' ')[0]

        except ValueError:
            return

        if not self.is_name_valid(app_name):
            return

        self.ua_data = {
            'name': app_name,
            'version': app_version
        }

        self.known = True

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
