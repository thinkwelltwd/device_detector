from urllib.parse import unquote
from ..base import ParserBaseTest
from ...parser import Camera, CarBrowser, Console, Notebook


class TestDeviceBase(ParserBaseTest):

    def test_parse(self):
        fixtures = self.load_fixtures()

        for fixture in fixtures:
            self.user_agent = unquote(fixture.pop('user_agent'))
            expect = fixture['device']
            spaceless = self.user_agent.lower().replace(' ', '')
            parsed = self.Parser(self.user_agent, spaceless, None).parse()

            data = parsed.ua_data

            for field in ('type', 'brand', 'model'):
                if field not in data:
                    continue
                self.assertEqual(
                    str(expect[field]),
                    str(data[field]),
                    field=field,
                )


class TestConsole(TestDeviceBase):

    fixture_files = [
        'tests/parser/fixtures/upstream/device/console.yml',
    ]
    Parser = Console


class TestCamera(TestDeviceBase):

    fixture_files = [
        'tests/parser/fixtures/upstream/device/camera.yml',
    ]
    Parser = Camera


class TestCarBrowser(TestDeviceBase):

    fixture_files = [
        'tests/parser/fixtures/upstream/device/car_browser.yml',
    ]
    Parser = CarBrowser


class TestNotebook(TestDeviceBase):

    fixture_files = [
        'tests/parser/fixtures/upstream/device/notebook.yml',
    ]
    Parser = Notebook


__all__ = [
    'TestConsole',
    'TestCamera',
    'TestCarBrowser',
    'TestNotebook',
]
