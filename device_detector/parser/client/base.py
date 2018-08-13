from ..parser import Parser


class BaseClientParser(Parser):

    def dtype(self):
        return self.cache_name.lower()



__all__ = (
    'BaseClientParser',
)
