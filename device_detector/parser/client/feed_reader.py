from . import BaseClientParser


class FeedReader(BaseClientParser):

    def dtype(self):
        return self.calculated_dtype or 'feed reader'

    fixture_files = [
        'upstream/client/feed_readers.yml',
    ]


__all__ = [
    'FeedReader',
]
