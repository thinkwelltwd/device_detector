from urllib.parse import unquote
from ..base import ParserBaseTest
from ...parser import OS, OSFragment, ClientHints
from ...utils import ua_hash


class TestOS(ParserBaseTest):

    fixture_files = [
        'tests/parser/fixtures/local/oss.yml',
        'tests/parser/fixtures/upstream/oss.yml',
    ]
    fields = ('name', 'version')
    fixture_key = 'os'
    Parser = OS


class TestOSFragment(ParserBaseTest):

    fixture_files = [
        'tests/parser/fixtures/local/osfragments.yml',
    ]
    fields = ('name',)
    fixture_key = 'name'

    def test_parsing(self):
        fixtures = self.load_fixtures()

        for fixture in fixtures:
            self.user_agent = unquote(fixture.pop('user_agent'))
            hashed = ua_hash(self.user_agent)
            spaceless = self.user_agent.lower().replace(' ', '')
            expect = fixture['name']
            parsed = OSFragment(
                self.user_agent,
                hashed,
                spaceless,
                client_hints=ClientHints.new(fixture.get('headers', {})),
            ).parse()

            self.assertEqual(expect, parsed.ua_data['name'])


__all__ = (
    'TestOS',
    'TestOSFragment',
)
