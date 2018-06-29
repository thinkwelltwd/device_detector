from . import BaseClientParser


class DesktopApp(BaseClientParser):

    fixture_files = [
        'local/client/osutility.yml',
        'local/client/antivirus.yml',
        'local/client/desktop_apps.yml',
    ]

    def dtype(self):
        return self.ua_data.get('type', 'desktop app')


__all__ = (
    'DesktopApp',
)
