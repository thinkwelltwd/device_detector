from . import BaseClientParser
from ..parser import ENDSWITH_DARWIN
from device_detector.enums import AppType


class MobileApp(BaseClientParser):
    __slots__ = ()
    APP_TYPE = AppType.MobileApp

    fixture_files = [
        'local/client/mobile_apps.yml',
        'upstream/client/mobile_apps.yml',
    ]

    def check_all_regexes(self) -> bool | list:
        # Don't check ahocorasick for user agents like:
        # R/3.6.0 (ubuntu-16.04) R (3.6.0 x86_64-pc-linux-gnu x86_64 linux-gnu)
        if self.user_agent_lower.startswith("r/"):
            return True
        if check_all := super().check_all_regexes():
            return check_all
        if ENDSWITH_DARWIN.search(self.user_agent_lower):
            return True
        return False


__all__ = [
    'MobileApp',
]
