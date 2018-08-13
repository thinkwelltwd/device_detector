from . import BaseClientParser


class Messaging(BaseClientParser):

    fixture_files = [
        'local/client/messaging.yml',
    ]

    def dtype(self):
        return 'messaging'



__all__ = (
    'Messaging',
)
