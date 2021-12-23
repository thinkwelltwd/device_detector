from . import BaseClientParser


class Messaging(BaseClientParser):

    def dtype(self):
        return self.calculated_dtype or 'messaging'


__all__ = [
    'Messaging',
]
