from . import BaseClientParser


class Library(BaseClientParser):

    fixture_files = [
        'local/client/libraries.yml',
        'upstream/client/libraries.yml',
    ]


__all__ = [
    'Library',
]
