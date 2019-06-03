from ..base import DetectorBaseTest
from ...device_detector import DeviceDetector


class TestNormalized(DetectorBaseTest):

    fixture_files = [
        'tests/fixtures/local/normalize.yml',
    ]

    def test_parsing(self):
        return

    def test_normalized(self):

        for fixture in self.load_fixtures():
            self.user_agent = fixture.pop('user_agent')
            device = DeviceDetector(self.user_agent)
            device.parse()

            self.assertEqual(device.pretty_name(), fixture['normalized'])


class TestDetectBot(DetectorBaseTest):

    fixture_files = [
        'tests/fixtures/upstream/bots.yml',
    ]


class TestDetectCamera(DetectorBaseTest):

    fixture_files = [
        'tests/fixtures/upstream/camera.yml',
    ]


class TestDetectCarBrowser(DetectorBaseTest):

    fixture_files = [
        'tests/fixtures/upstream/car_browser.yml',
    ]


class TestDetectConsole(DetectorBaseTest):

    fixture_files = [
        'tests/fixtures/upstream/console.yml',
    ]


class TestDetectDesktop(DetectorBaseTest):

    fixture_files = [
        'tests/fixtures/upstream/desktop.yml',
    ]


class TestDetectFeedReader(DetectorBaseTest):

    fixture_files = [
        'tests/fixtures/upstream/feed_reader.yml',
    ]


class TestDetectFeaturePhone(DetectorBaseTest):

    fixture_files = [
        'tests/fixtures/upstream/feature_phone.yml',
    ]


class TestDetectMediaPlayer(DetectorBaseTest):

    fixture_files = [
        'tests/fixtures/upstream/mediaplayer.yml',
    ]


class TestDetectMobileApps(DetectorBaseTest):

    fixture_files = [
        'tests/fixtures/upstream/mobile_apps.yml',
    ]


class TestDetectSmartPhone(DetectorBaseTest):

    fixture_files = [
        'tests/fixtures/upstream/smartphone.yml',
    ]


class TestDetectSmartPhone1(DetectorBaseTest):

    fixture_files = [
        'tests/fixtures/upstream/smartphone-1.yml',
    ]


class TestDetectSmartPhone2(DetectorBaseTest):

    fixture_files = [
        'tests/fixtures/upstream/smartphone-2.yml',
    ]


class TestDetectSmartPhone3(DetectorBaseTest):

    fixture_files = [
        'tests/fixtures/upstream/smartphone-3.yml',
    ]


class TestDetectSmartPhone4(DetectorBaseTest):

    fixture_files = [
        'tests/fixtures/upstream/smartphone-4.yml',
    ]


class TestDetectSmartPhone5(DetectorBaseTest):

    fixture_files = [
        'tests/fixtures/upstream/smartphone-5.yml',
    ]


class TestDetectTablet(DetectorBaseTest):

    fixture_files = [
        'tests/fixtures/upstream/tablet.yml',
    ]


class TestDetectTablet1(DetectorBaseTest):

    fixture_files = [
        'tests/fixtures/upstream/tablet-1.yml',
    ]


class TestDetectTablet2(DetectorBaseTest):

    fixture_files = [
        'tests/fixtures/upstream/tablet-2.yml',
    ]


class TestDetectTV(DetectorBaseTest):

    fixture_files = [
        'tests/fixtures/upstream/tv.yml',
    ]
