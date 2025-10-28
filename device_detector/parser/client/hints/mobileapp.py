from .. import BaseClientParser


class MobileAppHints(BaseClientParser):
    hints_fixture_files = [
        'upstream/client/hints/apps.yml',
    ]
