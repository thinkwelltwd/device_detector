from . import BaseClientParser
from device_detector.enums import AppType


class MediaPlayer(BaseClientParser):
    __slots__ = ()
    APP_TYPE = AppType.MediaPlayer

    fixture_files = [
        'local/client/mediaplayers.yml',
        'upstream/client/mediaplayers.yml',
    ]


__all__ = [
    'MediaPlayer',
]
