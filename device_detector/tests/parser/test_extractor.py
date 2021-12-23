from urllib.parse import unquote
from ..base import ParserBaseTest
from ...parser import (
    ApplicationIDExtractor,
    NameExtractor,
    ModelExtractor,
    VersionExtractor,
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
            expected = fixture['client']['app_id']
            app_id = ApplicationIDExtractor(self.user_agent)
            parsed = app_id.extract().get('app_id', '')

            self.assertEqual(expected, parsed, msg=error.format(self.user_agent, parsed, expected))

            expected = fixture['client']['pretty_name']
            parsed = app_id.pretty_name()
            self.assertEqual(expected, parsed, msg=error.format(self.user_agent, parsed, expected))


class TestNameExtractor(ParserBaseTest):

    def test_name(self):
        name = NameExtractor({'name': 'Candy $1'}, ['Cane']).extract()
        self.assertEqual(name, 'Candy Cane')

    def test_multiple_substitutions(self):
        name = NameExtractor({'name': 'Candy $1 ($2)'}, ['Cane', 'Curve']).extract()
        self.assertEqual(name, 'Candy Cane (Curve)')


class TestModelExtractor(ParserBaseTest):

    def test_underscore_substitution(self):
        model = ModelExtractor({'model': 'Candy_Canes'}, []).extract()
        self.assertEqual(model, 'Candy Canes')

    def test_substitutions(self):
        model = ModelExtractor({'model': 'Blu-ray Player (BDP$1)'}, [5600]).extract()
        self.assertEqual(model, 'Blu-ray Player (BDP5600)')


class TestVersionExtractor(ParserBaseTest):

    def test_underscore_substitution(self):
        version = VersionExtractor({'version': '8_2'}, []).extract()
        self.assertEqual(version, '8.2')

    def test_multiple_substitutions(self):
        version = VersionExtractor({'version': '$1 ($2)'}, [8, 5]).extract()
        self.assertEqual(version, '8 (5)')

    def test_trailing_dot(self):
        version = VersionExtractor({'version': '$1'}, ['2.']).extract()
        self.assertEqual(version, '2')


__all__ = (
    'TestApplicationIDExtractor',
    'TestNameExtractor',
    'TestModelExtractor',
    'TestVersionExtractor',
)
