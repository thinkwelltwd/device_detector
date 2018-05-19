from . import BaseClientParser


class FeedReader(BaseClientParser):

    def dtype(self):
        return 'feed reader'

    fixture_files = [
        'client/feed_readers.yml',
    ]



__all__ = (
    'FeedReader',
)
