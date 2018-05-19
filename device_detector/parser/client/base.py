from ..parser import Parser


class BaseClientParser(Parser):

    def dtype(self):
        return self.cache_name.lower()

    def set_details(self):
        super().set_details()
        if self.ua_data:
            self.ua_data.update({
                'type': self.dtype(),
            })



__all__ = (
    'BaseClientParser',
)
