from copy import deepcopy
import os


# interpolate regex with anchors so
# iPhone / Tiphone are matched correctly
BOUNDED_REGEX = '(?:^|[^A-Z0-9\_\-])(?:{})'

class Cache(dict):

    base = {
        'regexes': {},
        'user_agents': {},
    }

    def __init__(self, *args, **kwargs):
        kwargs.update(deepcopy(self.base))
        super().__init__(*args, **kwargs)

    def clear(self):
        super().clear()
        self.update(deepcopy(self.base))


ROOT = os.path.dirname(os.path.abspath(__file__))

DDCache = Cache()


__all__ = (
    'DDCache', 'ROOT', 'BOUNDED_REGEX',
)
