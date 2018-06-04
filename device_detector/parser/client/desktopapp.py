from . import BaseClientParser


class DesktopApp(BaseClientParser):

    fixture_files = [
        'client/osutility.yml',
        'client/antivirus.yml',
        'client/desktop_apps.yml',
    ]

    def dtype(self):
        return self.ua_data.get('type', 'desktop app')


__all__ = (
    'DesktopApp',
)
