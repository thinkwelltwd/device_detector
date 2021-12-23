from . import BaseClientParser


class MediaPlayer(BaseClientParser):

    fixture_files = [
        'local/client/mediaplayers.yml',
        'upstream/client/mediaplayers.yml',
    ]


__all__ = [
    'MediaPlayer',
]
