from . import BaseClientParser


class PIM(BaseClientParser):

    appdetails_files = [
        'appdetails/pim.yml',
    ]

    fixture_files = [
        'local/client/pim.yml',
        'upstream/client/pim.yml',
    ]


__all__ = [
    'PIM',
]
