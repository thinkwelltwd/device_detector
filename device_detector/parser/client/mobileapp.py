from . import BaseClientParser


class MobileApp(BaseClientParser):

    fixture_files = [
        'client/mobile_apps.yml',
    ]

    def dtype(self):
        return 'mobile app'



__all__ = (
    'MobileApp',
)
