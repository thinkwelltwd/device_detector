from .base import BaseDeviceParser
from device_detector.enums import DeviceType


class Bot(BaseDeviceParser):
    __slots__ = ()
    DEVICE_TYPE = DeviceType.Unknown

    fixture_files = [
        'upstream/bots.yml',
    ]

    def is_bot(self) -> bool:
        return self.matched_regex is not None

    def set_details(self) -> None:
        return super().set_details() if self.is_bot() else None


__all__ = [
    'Bot',
]
