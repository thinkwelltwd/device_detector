from .base import BaseDeviceParser
from device_detector.enums import DeviceType


class Camera(BaseDeviceParser):
    __slots__ = ()
    DEVICE_TYPE = DeviceType.Camera

    fixture_files = [
        'upstream/device/cameras.yml',
    ]

    def pre_process_regex_for_corasick(self, reg: str) -> str:
        reg = super().pre_process_regex_for_corasick(reg)
        if reg == 'EK-G[CN][0-9]{3}':
            return 'EK-G[CN][0-9]'
        return reg


__all__ = [
    'Camera',
]
