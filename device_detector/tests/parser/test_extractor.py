from urllib.parse import unquote
from ..base import ParserBaseTest
from ...parser import (
    ApplicationIDExtractor,
)


class TestApplicationIDExtractor(ParserBaseTest):

    fixture_files = [
        'tests/parser/fixtures/local/extractor/applicationid.yml',
        'tests/parser/fixtures/local/extractor/app_id_override_name.yml',
    ]

    def test_parsing(self):
        fixtures = self.load_fixtures()
        error = 'Error parsing {}.\n Parsed value "{}" != expected value "{}"'

        for fixture in fixtures:
            self.user_agent = unquote(fixture.pop('user_agent'))
            app_id = ApplicationIDExtractor(self.user_agent).extract()

            expected = fixture['client']['pretty_name']
            parsed = app_id.pretty_name()
            self.assertEqual(expected, parsed, msg=error.format(self.user_agent, parsed, expected))

__all__ = [
    'TestApplicationIDExtractor',
]
