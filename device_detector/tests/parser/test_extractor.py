from ..base import ParserBaseTest
from ...parser import NameExtractor, ModelExtractor, VersionExtractor



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
    'TestNameExtractor', 'TestModelExtractor', 'TestVersionExtractor',
)
