from . import BaseClientParser


class P2P(BaseClientParser):

    appdetails_files = [
        'appdetails/p2p.yml',
    ]

    fixture_files = [
        'local/client/p2p.yml',
    ]

    def dtype(self):
        return self.calculated_dtype or 'p2p'


__all__ = [
    'P2P',
]
