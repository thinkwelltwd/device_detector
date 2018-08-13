from . import BaseClientParser


class Game(BaseClientParser):

    fixture_files = [
        'local/client/games.yml',
    ]

    def dtype(self):
        return 'game'



__all__ = (
    'Game',
)
