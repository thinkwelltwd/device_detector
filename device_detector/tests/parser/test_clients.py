from ..base import ParserBaseTest
from ...parser import (
    Browser, DesktopApp, FeedReader, Library, MediaPlayer, MobileApp,
    DesktopApp, PIM,
)

class TestBrowser(ParserBaseTest):

    fixture_files = [
        'tests/parser/fixtures/client/browser.yml',
    ]
    fields = ('name', 'type', 'short_name', 'version')
    Parser = Browser


class TestFeedReader(ParserBaseTest):

    fixture_files = [
        'tests/parser/fixtures/client/feed_reader.yml',
    ]
    fields = ('name', 'type', 'version')
    Parser = FeedReader


class TestLibrary(ParserBaseTest):

    fixture_files = [
        'tests/parser/fixtures/client/library.yml',
    ]
    fields = ('name', 'type', 'version')
    Parser = Library


class TestMediaPlayer(ParserBaseTest):

    fixture_files = [
        'tests/parser/fixtures/client/mediaplayer.yml',
    ]
    fields = ('name', 'type', 'version')
    Parser = MediaPlayer


class TestMobileApp(ParserBaseTest):

    fixture_files = [
        'tests/parser/fixtures/client/mobile_app.yml',
    ]
    fields = ('name', 'type', 'version')
    Parser = MobileApp


class TestPIM(ParserBaseTest):

    fixture_files = [
        'tests/parser/fixtures/client/pim.yml',
    ]
    fields = ('name', 'type', 'version')
    Parser = PIM


class TestDesktopApp(ParserBaseTest):

    fixture_files = [
        'tests/parser/fixtures/client/antivirus.yml',
        'tests/parser/fixtures/client/osutility.yml',
        'tests/parser/fixtures/client/desktop_app.yml',
    ]
    fields = ('name', 'type', 'version')
    Parser = DesktopApp


__all__ = (
    'TestBrowser', 'TestDesktopApp', 'TestFeedReader', 'TestLibrary',
    'TestMediaPlayer', 'TestMobileApp', 'TestPIM',
)
