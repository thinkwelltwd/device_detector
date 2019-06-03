try:
    import regex as re
except (ImportError, ModuleNotFoundError):
    import re
import string

from ..parser import Parser
from ...settings import DDCache
from ...utils import version_from_key

keep = {'!', '@', '+'}
table = str.maketrans(dict.fromkeys(''.join(c for c in string.punctuation if c not in keep)))


class BaseClientParser(Parser):

    # Get the "full name/version" (space allowed) at beginning of UA string
    # merriam-webster dictionary/430.11 cfnetwork/893.14.2 darwin/17.3.0
    # Aurora HDR 2018/1.1.2 Sparkle/1.13.1
    # libreoffice 5.4.3.2 (92a7159f7e4af62137622921e809f8546db437e5; windows; x86;)
    # openoffice.org 3.2 (320m18(build:9502); windows; x86; bundledlanguages=en-us)
    FIRST_NAME_SLASH_VERSION = re.compile(
        r'^(?P<name>[\w\d\.\-_\&\'!®\?, \+]+)[\/( \-][vr]?(?P<version>[\d\.]+)\b',
        re.IGNORECASE,
    )

    # Get the "name version" (space allowed) at beginning of UA string
    # CarboniteDownloader 6.3.2 build 7466 (Sep-07-2017)
    # Microsoft Office Access 2013 (15.0.4693) Windows NT 6.2
    NAME_SPACE_VERSION = re.compile(
        r'^(?P<name>[\w\d\.\-_\&\'!®\?,\+]+) v?(?P<version>[\d\.]+)',
        re.IGNORECASE,
    )

    # Name can't include space after the first match. IOW, don't want to extract
    # "NRD90M Android/7.0" from the following regex
    # Version/1 Yelp/v9.16.1 Carrier/AT&T Model/j7popelteatt OSBuild/NRD90M Android/7.0
    NAME_SLASH_VERSION = re.compile(
        r'\b(?P<name>[\w\d\-_\.\&\'!®\?\+]+)[\/]v?(?P<version>[\d\.]+)',
        re.IGNORECASE,
    )

    FIRST_ALPHANUMERIC_WORD = re.compile(r'^([a-z0-9]+)', re.IGNORECASE)

    def name_version_pairs(self) -> list:
        """
        This regex used on most UA strings so we don't need to write the same
        <name>/<version> regexes over and again

        Try to find interesting matches with name/version or name (version) format
        anywhere in the regex, skipping the obvious cruft.

        Zip Books/1.3.20 (com.zipbooks.zipbooksios; build:1309; iOS 12.1.3) Alamofire/4.3.0
        should return - [('zipbooks', 'Zip Books', '1.3.20'), ('alamofire', 'Alamofire', '4.3.0')]

        Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Spotify/1.0.92.390 Safari/537.36
        should return - [('spotify', 'Spotify', '1.0.92.390'), ('safari', 'Safari', '537.36')]

        Mozilla/5.0 (Windows NT 10.0: WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36 Avast/69.0.792.81
        should return - [('chrome', 'Chrome', '69.0.3497.81'), ('safari', 'Safari', '537.36'), ('avast', 'Avast', '69.0.792.81')]
        """
        from .browser import CRUFT_NAMES
        ua = self.user_agent

        cached = DDCache['user_agents'][self.ua_hash].get('name_version_pairs', [])
        if cached:
            return cached

        matches = self.FIRST_NAME_SLASH_VERSION.findall(ua)
        matches.extend(self.NAME_SPACE_VERSION.findall(ua))

        first_slash = self.user_agent.find('/')
        matches.extend(self.NAME_SLASH_VERSION.findall(ua, pos=first_slash + 1))

        cleaned_matches = []

        for name, version in matches:
            name = name.strip()
            name_lower = name.lower()
            if name_lower in CRUFT_NAMES:
                continue
            code = name_lower.replace(' ', '')
            cleaned_matches.append((code, name, version.strip()))

        DDCache['user_agents'][self.ua_hash]['name_version_pairs'] = cleaned_matches
        return cleaned_matches

    def _parse(self) -> None:
        """
        Check the name_version_pairs data before checking regexes
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
                return

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
            return

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
        if self.calculated_dtype:
            return self.calculated_dtype

        app_name_lower = self.app_name.lower()
        for name, dtype in (
            ('update', 'desktop app'),
            ('api', 'library'),
            ('sdk', 'library'),
        ):
            if name in app_name_lower:
                return dtype

        return 'generic'


__all__ = (
    'BaseClientParser',
    'GenericClientParser',
)
