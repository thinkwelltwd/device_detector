from ..base import ParserBaseTest
from ...parser import Device
from ...utils import ua_hash


class TestDevices(ParserBaseTest):

    fixture_files = [
        'tests/parser/fixtures/upstream/device/console.yml',
        'tests/parser/fixtures/upstream/device/car_browser.yml',
        'tests/parser/fixtures/upstream/device/camera.yml',
    ]
    Parser = Device

    def test_parse(self):
        fixtures = self.load_fixtures()

        for fixture in fixtures:
            self.user_agent = fixture.pop('user_agent')
            expect = fixture['device']
            hashed = ua_hash(self.user_agent)
            spaceless = self.user_agent.lower().replace(' ', '')
            parsed = Device(self.user_agent, hashed, spaceless).parse()

            data = parsed.ua_data
            data['type'] = Device.DEVICE_TYPES[data['type']]

            for field in ('type', 'brand', 'model'):
                self.assertEqual(
                    str(expect[field]),
                    str(data[field]),
                    msg='Error parsing {}. \n'
                    'Field "{}" parsed value "{}" != expected value "{}"'.format(
                        self.user_agent, field, data[field], expect[field]
                    )
                )


__all__ = [
    'TestDevices',
]
