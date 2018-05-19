from . import BaseClientParser


class Library(BaseClientParser):

    fixture_files = [
        'client/libraries.yml',
    ]



__all__ = (
    'Library',
)
