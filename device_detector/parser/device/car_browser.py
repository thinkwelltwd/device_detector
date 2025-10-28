from .base import BaseDeviceParser
from device_detector.enums import DeviceType


class CarBrowser(BaseDeviceParser):
    __slots__ = ()
    DEVICE_TYPE = DeviceType.CarBrowser

    fixture_files = [
        'upstream/device/car_browsers.yml',
    ]


__all__ = [
    'CarBrowser',
]
