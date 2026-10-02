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

    def test_no_appid(self):
        for ua in (
            'RCAppMobile/26 (RingCentral; iPhone 14; iOS/26; build.1090; rev.dc64d57511a)',
        ):
            app_id = ApplicationIDExtractor(ua).extract()
            self.assertIsNone(app_id.details.get('app_id'), msg=f'No found AppID in {ua!r}')


__all__ = [
    'TestApplicationIDExtractor',
]
