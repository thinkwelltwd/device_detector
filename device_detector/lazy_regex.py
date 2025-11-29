from urllib.parse import unquote
import regex
from regex import IGNORECASE


# When one of these attributes is called, compile the regex
REGEX_ATTRS = {
    'match',
    'fullmatch',
    'search',
    'sub',
    'subf',
    'subfn',
    'split',
    'splititer',
    'findall',
    'finditer',
    'purge',
    'escape',
    'compiled',
}


class RegexLazy:
    """
    Defer compilation of regex until it's actually called.
    Some regexes, especially on device models will almost
    never be called, so save the compilation time.
    """

    def __init__(self, pattern: str, flags: int = 0) -> None:
        # Decode UA regexes because UA strings are also decoded
        # Pic%20Collage/(\d+[\.\d]+) CFNetwork
        self.pattern = unquote(pattern)
        self.flags = flags
        self.compiled = None

    def __getattribute__(self, attribute: str) -> regex.Regex:
        compiled_regex = super().__getattribute__('compiled')
        if compiled_regex is None and attribute in REGEX_ATTRS:
            pattern = super().__getattribute__('pattern')
            flags = super().__getattribute__('flags')
            compiled_regex = regex.compile(pattern, flags)
            self.compiled = compiled_regex

        if attribute == 'compiled':
            return compiled_regex

        return getattr(compiled_regex, attribute)

    def __repr__(self) -> str:
        return repr(self.compiled)

    def __hash__(self) -> int:
        return hash(self.compiled)

    def __eq__(self, other: regex.Regex) -> bool:
        return self.compiled == other.compiled


class RegexLazyIgnore(RegexLazy):
    def __init__(self, pattern: str) -> None:
        super().__init__(pattern, IGNORECASE)


__all__ = (
    'RegexLazy',
    'RegexLazyIgnore',
)
