from .base import BaseDeviceParser
from device_detector.enums import DeviceType

# Extracted from ^(?:chrome|firefox|Abcd|Dark|KvshClient|Node.js|Report Runner|url|Zeus|ZmEu)$
GENERIC_BOT_UAS = {
    'chrome',
    'firefox',
    'abcd',
    'dark',
    'kvshclient',
    'node.js',
    'report runner',
    'url',
    'zeus',
    'zmeu',
    'google',
}


class Bot(BaseDeviceParser):
    __slots__ = ()
    DEVICE_TYPE = DeviceType.Unknown

    fixture_files = [
        'upstream/bots.yml',
    ]

    def check_all_regexes(self) -> bool | list:
        if check_all := super().check_all_regexes():
            return check_all
        return self.user_agent.lower() in GENERIC_BOT_UAS

    def is_bot(self) -> bool:
        return self.matched_regex is not None

    def set_details(self) -> None:
        return super().set_details() if self.is_bot() else None


__all__ = [
    'Bot',
]
