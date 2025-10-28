from .base import BaseDeviceParser
from device_detector.enums import DeviceType


class Camera(BaseDeviceParser):
    __slots__ = ()
    DEVICE_TYPE = DeviceType.Camera

    fixture_files = [
        'upstream/device/cameras.yml',
    ]


__all__ = [
    'Camera',
]
