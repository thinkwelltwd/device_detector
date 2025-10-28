from . import BaseClientParser
from device_detector.enums import AppType


class MobileApp(BaseClientParser):
    __slots__ = ()
    APP_TYPE = AppType.MobileApp

    fixture_files = [
        'upstream/client/mobile_apps.yml',
    ]


__all__ = [
    'MobileApp',
]
