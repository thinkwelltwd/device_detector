from . import BaseClientParser


class Game(BaseClientParser):

    appdetails_files = [
        'appdetails/games.yml',
    ]

    fixture_files = [
        'local/client/games.yml',
    ]

    def dtype(self):
        return self.calculated_dtype or 'game'


__all__ = [
    'Game',
]
