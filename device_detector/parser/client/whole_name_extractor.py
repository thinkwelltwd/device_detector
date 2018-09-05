from . import BaseClientParser


class WholeNameExtractor(BaseClientParser):
    """
    Catch all for user agents that do not use the slash format
    """

# -------------------------------------------------------------------
    # App names that have no value to us so we want to discard them
    # Should be lowercase
    discard = {
        '15b93',
        '15d100',
        '15e216',
        '16a5365b',
        '15g77'
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
    app_name = ''

    def _parse(self):
        if '/' in self.user_agent:
            return

        self.app_name = self.remove_punctuation(self.user_agent)

        if self.discard_name():
            return

        self.ua_data = {'name': self.app_name}

        self.known = True

    def dtype(self) -> str:
        return 'generic'
