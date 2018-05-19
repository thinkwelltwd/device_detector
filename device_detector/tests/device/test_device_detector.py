from ..base import DetectorBaseTest
from ... import DeviceDetector


class TestDetectBot(DetectorBaseTest):

    fixture_files = [
        'tests/fixtures/bots.yml',
    ]
    Parser = DeviceDetector


class TestDetectCamera(DetectorBaseTest):

    fixture_files = [
        'tests/fixtures/camera.yml',
    ]
    Parser = DeviceDetector


class TestDetectCarBrowser(DetectorBaseTest):

    fixture_files = [
        'tests/fixtures/car_browser.yml',
    ]
    Parser = DeviceDetector


class TestDetectConsole(DetectorBaseTest):

    fixture_files = [
        'tests/fixtures/console.yml',
    ]
    Parser = DeviceDetector


class TestDetectDesktop(DetectorBaseTest):

    fixture_files = [
        'tests/fixtures/desktop.yml',
    ]
    Parser = DeviceDetector


class TestDetectFeedReader(DetectorBaseTest):

    fixture_files = [
        'tests/fixtures/feed_reader.yml',
    ]
    Parser = DeviceDetector


class TestDetectFeaturePhone(DetectorBaseTest):

    fixture_files = [
        'tests/fixtures/feature_phone.yml',
    ]
    Parser = DeviceDetector


class TestDetectMediaPlayer(DetectorBaseTest):

    fixture_files = [
        'tests/fixtures/mediaplayer.yml',
    ]
    Parser = DeviceDetector


class TestDetectMobileApps(DetectorBaseTest):

    fixture_files = [
        'tests/fixtures/mobile_apps.yml',
    ]
    Parser = DeviceDetector


class TestDetectSmartPhone(DetectorBaseTest):

    fixture_files = [
        'tests/fixtures/smartphone.yml',
    ]
    Parser = DeviceDetector


class TestDetectSmartPhone1(DetectorBaseTest):

    fixture_files = [
        'tests/fixtures/smartphone-1.yml',
    ]
    Parser = DeviceDetector


class TestDetectSmartPhone4(DetectorBaseTest):

    fixture_files = [
        'tests/fixtures/smartphone-4.yml',
    ]
    Parser = DeviceDetector


class TestDetectSmartPhone5(DetectorBaseTest):

    fixture_files = [
        'tests/fixtures/smartphone-5.yml',
    ]
    Parser = DeviceDetector


class TestDetectTablet(DetectorBaseTest):

    fixture_files = [
        'tests/fixtures/tablet.yml',
    ]
    Parser = DeviceDetector


class TestDetectTablet1(DetectorBaseTest):

    fixture_files = [
        'tests/fixtures/tablet-1.yml',
    ]
    Parser = DeviceDetector


class TestDetectTablet2(DetectorBaseTest):

    fixture_files = [
        'tests/fixtures/tablet-2.yml',
    ]
    Parser = DeviceDetector


class TestDetectTV(DetectorBaseTest):

    fixture_files = [
        'tests/fixtures/tv.yml',
    ]
    Parser = DeviceDetector
