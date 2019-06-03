from . import BaseClientParser


class Messaging(BaseClientParser):

    appdetails_files = [
        'appdetails/messaging.yml',
    ]

    def dtype(self):
        return self.calculated_dtype or 'messaging'


__all__ = [
    'Messaging',
]
