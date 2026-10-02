from ..base import DetectorBaseTest


class TestDetectConsole(DetectorBaseTest):

    fixture_files = [
        'tests/fixtures/upstream/console.yml',
    ]


class TestDetectPodcasting(DetectorBaseTest):

    fixture_files = [
        'tests/fixtures/upstream/podcasting.yml',
    ]


class TestDetectMediaPlayer(DetectorBaseTest):

    fixture_files = [
        'tests/fixtures/upstream/mediaplayer.yml',
    ]


class TestDetectSmartSpeaker(DetectorBaseTest):

    fixture_files = [
        'tests/fixtures/upstream/smart_speaker.yml',
    ]
