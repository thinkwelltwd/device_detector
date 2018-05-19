from . import BaseClientParser


class PIM(BaseClientParser):

    fixture_files = [
        'client/pim.yml',
    ]



__all__ = (
    'PIM',
)
