from ..parser import Parser
import string

keep = {'!', '@', '+'}
table = str.maketrans(dict.fromkeys(''.join(c for c in string.punctuation if c not in keep)))


class BaseClientParser(Parser):

    def discard_name(self) -> bool:
        """
        Determine if app name is of any value to us

        Return True if app should be discarded
        """

        if not self.is_name_length_valid():
            return True

        if self.app_name.lower() in self.discard:
            return True

        if self.is_substring_unwanted():
            return True

        if self.unwanted_regex_match():
            return True

        return self.is_name_mostly_numeric()

    def is_name_length_valid(self) -> bool:
        """
        Check if app name portion of UA is between 3 and 25 chars
        """
        return 2 < len(self.app_name) < 26


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
        it has one or fewer alphabetic characters
        """

        s = self.remove_punctuation(self.app_name)

        try:
            int(s)
            return True
        except ValueError:
            pass

        alphabetic_chars = 0
        for char in s:
            if not char.isnumeric():
                alphabetic_chars += 1

        return alphabetic_chars < 2

    @staticmethod
    def remove_punctuation(string_with_punct: str) -> str:
        """
        Remove punctuation from the given string and return
        the new string
        """

        return string_with_punct.translate(table)

    def dtype(self):
        return self.cache_name.lower()


__all__ = (
    'BaseClientParser',
)
