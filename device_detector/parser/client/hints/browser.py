from .. import BaseClientParser


class BrowserHints(BaseClientParser):
    hints_fixture_files = [
        'upstream/client/hints/browsers.yml',
    ]
