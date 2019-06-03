from . import BaseClientParser


class MediaPlayer(BaseClientParser):

    appdetails_files = [
        'appdetails/mediaplayers.yml',
    ]

    fixture_files = [
        'upstream/client/mediaplayers.yml',
    ]


__all__ = [
    'MediaPlayer',
]
