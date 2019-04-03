from .base import BaseDeviceParser


class Bot(BaseDeviceParser):

    fixture_files = [
        'upstream/bots.yml',
    ]

    def is_bot(self) -> bool:
        return self.matched_regex is not None


__all__ = [
    'Bot',
]
