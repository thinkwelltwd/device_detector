from ..base import ParserBaseTest
from ...parser import VendorFragment


class TestVendorFragment(ParserBaseTest):

    fixture_files = [
        'tests/parser/fixtures/upstream/vendorfragments.yml',
    ]

    def test_parsing(self):
        fixtures = self.load_fixtures()

        for fixture in fixtures:
            self.user_agent = fixture.pop('useragent')
            expect = fixture['vendor']
            parsed = VendorFragment(self.user_agent).parse()
            self.assertEqual(expect, parsed.ua_data['brand'])



__all__ = (
    'TestVendorFragment',
)
