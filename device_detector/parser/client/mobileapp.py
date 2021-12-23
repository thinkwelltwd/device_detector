from . import BaseClientParser


class MobileApp(BaseClientParser):

    fixture_files = [
        'local/client/mobile_apps.yml',
        'upstream/client/mobile_apps.yml',
    ]

    def dtype(self):
        return self.calculated_dtype or 'mobile app'


__all__ = [
    'MobileApp',
]
