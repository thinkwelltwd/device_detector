from . import BaseClientParser
from device_detector.enums import AppType


class FeedReader(BaseClientParser):
    __slots__ = ()
    APP_TYPE = AppType.FeedReader

    fixture_files = [
        'upstream/client/feed_readers.yml',
    ]


__all__ = [
    'FeedReader',
]
