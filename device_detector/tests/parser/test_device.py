from urllib.parse import unquote
from ..base import ParserBaseTest
from ...parser import Device
from ...utils import ua_hash


class TestDevices(ParserBaseTest):

    fixture_files = [
        'tests/parser/fixtures/upstream/device/console.yml',
        'tests/parser/fixtures/upstream/device/car_browser.yml',
        'tests/parser/fixtures/upstream/device/camera.yml',
        'tests/parser/fixtures/upstream/device/notebook.yml',
    ]
    Parser = Device

    def test_parse(self):
        fixtures = self.load_fixtures()

        for fixture in fixtures:
            self.user_agent = unquote(fixture.pop('user_agent'))
            expect = fixture['device']
            hashed = ua_hash(self.user_agent)
            spaceless = self.user_agent.lower().replace(' ', '')
            parsed = Device(self.user_agent, hashed, spaceless, self.VERSION_TRUNCATION).parse()

            data = parsed.ua_data

            for field in ('type', 'brand', 'model'):
                if field not in data:
                    continue
                self.assertEqual(
                    str(expect[field]),
                    str(data[field]),
                    field=field,
                )


__all__ = [
    'TestDevices',
]
