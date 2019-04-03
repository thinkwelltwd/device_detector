from . import BaseClientParser


class PIM(BaseClientParser):

    fixture_files = [
        'local/client/pim.yml',
        'upstream/client/pim.yml',
    ]


__all__ = [
    'PIM',
]
