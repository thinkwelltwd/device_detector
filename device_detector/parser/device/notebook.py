from .base import BaseDeviceParser
from device_detector.enums import DeviceType
from ...lazy_regex import RegexLazy
from ...settings import BOUNDED_REGEX

FACEBOOK_NOTEBOOK_FRAGMENT = RegexLazy(BOUNDED_REGEX.format('FBMD/'))


class Notebook(BaseDeviceParser):
    __slots__ = ()
    DEVICE_TYPE = DeviceType.Desktop

    fixture_files = [
        'upstream/device/notebooks.yml',
    ]

    def _parse(self) -> None:
        """
        Loop through all brands of all device types trying to find
        a model. Returns the first device with model info.
        """
        if FACEBOOK_NOTEBOOK_FRAGMENT.search(self.user_agent):
            return super()._parse()


__all__ = [
    'Notebook',
]
