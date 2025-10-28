from . import BaseClientParser
from device_detector.enums import AppType


class Library(BaseClientParser):
    __slots__ = ()
    APP_TYPE = AppType.Library

    fixture_files = [
        'local/client/libraries.yml',
        'upstream/client/libraries.yml',
    ]


__all__ = [
    'Library',
]
