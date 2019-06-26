try:
    import regex as re
except (ImportError, ModuleNotFoundError):
    import re
import string

from ..parser import Parser
from ...parser.key_value_pairs import key_value_pairs
from ...settings import DDCache
from ...utils import version_from_key, calculate_dtype

keep = {'!', '@', '+'}
table = str.maketrans(dict.fromkeys(''.join(c for c in string.punctuation if c not in keep)))


class BaseClientParser(Parser):

    FIRST_ALPHANUMERIC_WORD = re.compile(r'^([a-z0-9]+)', re.IGNORECASE)

    def name_version_pairs(self) -> list:

        cached = DDCache['user_agents'][self.ua_hash].get('name_version_pairs', [])
        if cached:
            return cached

        name_version_pairs = key_value_pairs(ua=self.user_agent)

        DDCache['user_agents'][self.ua_hash]['name_version_pairs'] = name_version_pairs
        return name_version_pairs

    def matches_manual_appdetails(self):
        """
        Check the name_version_pairs data before checking regexes.

        Much faster to check for set membership than to iterate over
        custom regexes for each application.
        """
        app_details = self.appdetails_data
        name_version_pairs = self.name_version_pairs()

        for code, name, version in name_version_pairs:
            if code in app_details:
                self.known = True
                self.ua_data = {
                    'name': app_details[code]['name'],
                    # get version by Key/Value if it exists - News/582.1 Version/2.0
                    'version': version_from_key(name_version_pairs, version),
                }
                self.calculated_dtype = app_details[code].get('type', '')
                return True

        # check if whole UA string found in app details
        match = app_details.get(self.ua_spaceless, {})

        # Check if first alphanumeric word found in app details.
        if not match:
            try:
                first_word = self.FIRST_ALPHANUMERIC_WORD.search(self.ua_spaceless).group()
                match = app_details.get(first_word, {})
            except AttributeError:
                pass

        if match:
            match['version'] = None
            self.ua_data = match
            self.calculated_dtype = match.get('type', '')
            return True

        return False

    def _parse(self) -> None:
        """
        Each subclass may have `appdetails/<name>.yml` file(s) defined
        containing manually specified details for the regex.

        These files before checking regexes, for best performance.
        """
        manually_specified = self.matches_manual_appdetails()
        if not manually_specified:
            return super()._parse()


class GenericClientParser(BaseClientParser):

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
        alphabetic characters are less than 50% of the string
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

        return alphabetic_chars / len(app_no_punc) < .5

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
            m = regex.match(self.user_agent)

            if m:
                try:
                    self.app_name = m.group(group).strip()
                    return
                except Exception:
                    continue

        self.app_name = self.user_agent

    def dtype(self) -> str:
        if self.calculated_dtype:
            return self.calculated_dtype

        return calculate_dtype(app_name=self.app_name)


__all__ = (
    'BaseClientParser',
    'GenericClientParser',
)
