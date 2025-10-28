from . import BaseClientParser
from device_detector.enums import AppType


class Messaging(BaseClientParser):
    __slots__ = ()
    APP_TYPE = AppType.Messaging


__all__ = [
    'Messaging',
]
