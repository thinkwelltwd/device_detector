from .base import BaseDeviceParser
from device_detector.enums import DeviceType


class Console(BaseDeviceParser):
    __slots__ = ()
    DEVICE_TYPE = DeviceType.Console

    fixture_files = [
        'upstream/device/consoles.yml',
    ]


__all__ = [
    'Console',
]
