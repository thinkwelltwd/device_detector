from . import BaseClientParser
import re


class WholeNameExtractor(BaseClientParser):
    """
    Catch all for user agents that do not use the slash format
    """

# -------------------------------------------------------------------
    # App names that have no value to us so we want to discard them
    # Should be lowercase
    discard = {

    }

# -------------------------------------------------------------------
    # List of substrings that if found in the app name, we will
    # discard the entire app name
    # Should be lowercase
    unwanted_substrings = [

    ]

# -------------------------------------------------------------------
    # Regexes that we use to remove unwanted app names
    remove_unwanted_regex = [

    ]

# -------------------------------------------------------------------
    # Regexes that we use to extract app versions
    extract_version_regex = [
        (re.compile(r'(v?[\.\d]+$)', re.IGNORECASE)),
    ]

# -------------------------------------------------------------------
    app_name = ''
    app_version = ''

    def _parse(self):
        if '/' in self.user_agent:
            return

        ua_without_suffix = self.extract_version_suffix().strip()

        self.app_name = self.remove_punctuation(ua_without_suffix)

        if self.discard_name():
            return

        self.ua_data = {
            'name': self.app_name,
            'version': self.app_version
        }

        self.known = True

    def extract_version_suffix(self) -> str:
        """
        Check if app name has a suffix with the version number and
        extract if it does.  Return the UA string without the suffix.
        """

        for regex in self.extract_version_regex:

            match = regex.search(self.user_agent)

            if match:
                self.app_version = match.group()

                return self.user_agent[:match.start()]

            return self.user_agent

    def is_name_length_valid(self) -> bool:
        """
        Check if app name portion of UA is between 3 and 60 chars
        """

        if 2 < len(self.app_name) < 61:
            return True

        return False

    def dtype(self) -> str:
        return 'generic'
