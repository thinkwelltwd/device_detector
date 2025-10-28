from . import BaseClientParser
from device_detector.enums import AppType


class PIM(BaseClientParser):
    __slots__ = ()
    APP_TYPE = AppType.PIM

    fixture_files = [
        'upstream/client/pim.yml',
    ]


__all__ = [
    'PIM',
]
