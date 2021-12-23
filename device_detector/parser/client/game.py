from . import BaseClientParser


class Game(BaseClientParser):

    fixture_files = [
        'local/client/games.yml',
    ]

    def dtype(self):
        return self.calculated_dtype or 'game'


__all__ = [
    'Game',
]
