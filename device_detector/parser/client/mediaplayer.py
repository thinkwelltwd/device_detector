from . import BaseClientParser


class MediaPlayer(BaseClientParser):

    fixture_files = [
        'client/mediaplayers.yml',
    ]



__all__ = (
    'MediaPlayer',
)
