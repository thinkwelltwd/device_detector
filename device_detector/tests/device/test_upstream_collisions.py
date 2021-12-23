from urllib.parse import unquote
from ..base import DetectorBaseTest
from device_detector import DeviceDetector
from device_detector.device_detector import VERSION_TRUNCATION_NONE


class TestCollisions(DetectorBaseTest):
    """
    Upstream regexes may be too generic and collide with
    other mobile apps, so those fixtures may need to be
    removed or otherwise resolved.

    For example, the following regex is too lenient:

    #Firefox Focus / Firefox Klar
    - regex: '(?:Focus|Klar)(?:/(\d+[\.\d]+))?'
      name: 'Firefox Focus'
      version: '$1'
    """

    fixture_files = [
        'tests/parser/fixtures/local/collisions.yml',
    ]
    VERSION_TRUNCATION = VERSION_TRUNCATION_NONE

    def test_parsing(self):

        for fixture in self.load_fixtures():
            self.user_agent = unquote(fixture.pop('user_agent'))
            device = DeviceDetector(self.user_agent)
            device.parse()

            parsed = device.client_name()
            fixture = fixture['client']['name']
            self.assertEqual(
                parsed,
                fixture,
                msg=f'{parsed!r} should be {fixture!r}! You may need to edit upstream fixtures.',
            )
