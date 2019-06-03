from . import BaseClientParser


class Library(BaseClientParser):

    appdetails_files = [
        'appdetails/libraries.yml',
    ]

    fixture_files = [
        'local/client/libraries.yml',
        'upstream/client/libraries.yml',
    ]


__all__ = [
    'Library',
]
