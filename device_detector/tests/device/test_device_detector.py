from ..base import DetectorBaseTest
from ... import DeviceDetector


class TestDetectBot(DetectorBaseTest):

    fixture_files = [
        'tests/fixtures/upstream/bots.yml',
    ]
    Parser = DeviceDetector


class TestDetectCamera(DetectorBaseTest):

    fixture_files = [
        'tests/fixtures/upstream/camera.yml',
    ]
    Parser = DeviceDetector


class TestDetectCarBrowser(DetectorBaseTest):

    fixture_files = [
        'tests/fixtures/upstream/car_browser.yml',
    ]
    Parser = DeviceDetector


class TestDetectConsole(DetectorBaseTest):

    fixture_files = [
        'tests/fixtures/upstream/console.yml',
    ]
    Parser = DeviceDetector


class TestDetectDesktop(DetectorBaseTest):

    fixture_files = [
        'tests/fixtures/upstream/desktop.yml',
    ]
    Parser = DeviceDetector


class TestDetectFeedReader(DetectorBaseTest):

    fixture_files = [
        'tests/fixtures/upstream/feed_reader.yml',
    ]
    Parser = DeviceDetector


class TestDetectFeaturePhone(DetectorBaseTest):

    fixture_files = [
        'tests/fixtures/upstream/feature_phone.yml',
    ]
    Parser = DeviceDetector


class TestDetectMediaPlayer(DetectorBaseTest):

    fixture_files = [
        'tests/fixtures/upstream/mediaplayer.yml',
    ]
    Parser = DeviceDetector


class TestDetectMobileApps(DetectorBaseTest):

    fixture_files = [
        'tests/fixtures/upstream/mobile_apps.yml',
    ]
    Parser = DeviceDetector


class TestDetectSmartPhone(DetectorBaseTest):

    fixture_files = [
        'tests/fixtures/upstream/smartphone.yml',
    ]
    Parser = DeviceDetector


class TestDetectSmartPhone1(DetectorBaseTest):

    fixture_files = [
        'tests/fixtures/upstream/smartphone-1.yml',
    ]
    Parser = DeviceDetector


class TestDetectSmartPhone4(DetectorBaseTest):

    fixture_files = [
        'tests/fixtures/upstream/smartphone-4.yml',
    ]
    Parser = DeviceDetector


class TestDetectSmartPhone5(DetectorBaseTest):

    fixture_files = [
        'tests/fixtures/upstream/smartphone-5.yml',
    ]
    Parser = DeviceDetector


class TestDetectTablet(DetectorBaseTest):

    fixture_files = [
        'tests/fixtures/upstream/tablet.yml',
    ]
    Parser = DeviceDetector


class TestDetectTablet1(DetectorBaseTest):

    fixture_files = [
        'tests/fixtures/upstream/tablet-1.yml',
    ]
    Parser = DeviceDetector


class TestDetectTablet2(DetectorBaseTest):

    fixture_files = [
        'tests/fixtures/upstream/tablet-2.yml',
    ]
    Parser = DeviceDetector


class TestDetectTV(DetectorBaseTest):

    fixture_files = [
        'tests/fixtures/upstream/tv.yml',
    ]
    Parser = DeviceDetector
