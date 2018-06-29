from ..base import ParserBaseTest
from ...parser import (
    Browser,
    DesktopApp,
    FeedReader,
    Library,
    MediaPlayer,
    MobileApp,
    PIM,
)

class TestBrowser(ParserBaseTest):

    fixture_files = [
        'tests/parser/fixtures/local/client/browser.yml',
        'tests/parser/fixtures/upstream/client/browser.yml',
    ]
    fields = ('name', 'type', 'short_name', 'version')
    Parser = Browser


class TestFeedReader(ParserBaseTest):

    fixture_files = [
        'tests/parser/fixtures/upstream/client/feed_reader.yml',
    ]
    fields = ('name', 'type', 'version')
    Parser = FeedReader


class TestLibrary(ParserBaseTest):

    fixture_files = [
        'tests/parser/fixtures/local/client/library.yml',
        'tests/parser/fixtures/upstream/client/library.yml',
    ]
    fields = ('name', 'type', 'version')
    Parser = Library


class TestMediaPlayer(ParserBaseTest):

    fixture_files = [
        'tests/parser/fixtures/local/client/mediaplayer.yml',
        'tests/parser/fixtures/upstream/client/mediaplayer.yml',
    ]
    fields = ('name', 'type', 'version')
    Parser = MediaPlayer


class TestMobileApp(ParserBaseTest):

    fixture_files = [
        'tests/parser/fixtures/local/client/mobile_app.yml',
        'tests/parser/fixtures/upstream/client/mobile_app.yml',
    ]
    fields = ('name', 'type', 'version')
    Parser = MobileApp


class TestPIM(ParserBaseTest):

    fixture_files = [
        'tests/parser/fixtures/local/client/pim.yml',
        'tests/parser/fixtures/upstream/client/pim.yml',
    ]
    fields = ('name', 'type', 'version')
    Parser = PIM


class TestDesktopApp(ParserBaseTest):

    fixture_files = [
        'tests/parser/fixtures/local/client/antivirus.yml',
        'tests/parser/fixtures/local/client/osutility.yml',
        'tests/parser/fixtures/local/client/desktop_app.yml',
    ]
    fields = ('name', 'type', 'version')
    Parser = DesktopApp


__all__ = (
    'TestBrowser',
    'TestDesktopApp',
    'TestFeedReader',
    'TestLibrary',
    'TestMediaPlayer',
    'TestMobileApp',
    'TestPIM',
)
