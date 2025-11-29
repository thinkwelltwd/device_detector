from urllib.parse import unquote
from ..base import ParserBaseTest
from ...parser import VendorFragment


class TestVendorFragment(ParserBaseTest):

    fixture_files = [
        'tests/parser/fixtures/upstream/vendorfragments.yml',
    ]

    def test_parsing(self):
        fixtures = self.load_fixtures()

        for fixture in fixtures:
            self.user_agent = unquote(fixture.pop('useragent'))
            spaceless = self.user_agent.lower().replace(' ', '')
            expect = fixture['vendor']
            parsed = VendorFragment(self.user_agent, spaceless, None).parse()
            self.assertEqual(expect, parsed.ua_data['brand'])


__all__ = [
    'TestVendorFragment',
]
