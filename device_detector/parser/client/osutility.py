from . import BaseClientParser


class OSUtility(BaseClientParser):

    fixture_files = [
        'client/osutility.yml',
        'client/antivirus.yml',
    ]

    def dtype(self):
        return self.ua_data.get('type', 'osutility')


__all__ = (
    'OSUtility',
)
