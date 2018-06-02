from ..base import ParserBaseTest
from ...parser import (
    Browser, FeedReader, Library, MediaPlayer, MobileApp,
    OSUtility, PIM,
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


class TestOSUtility(ParserBaseTest):

    fixture_files = [
        'tests/parser/fixtures/client/osutility.yml',
    ]
    fields = ('name', 'type', 'version')
    Parser = OSUtility


__all__ = (
    'TestBrowser', 'TestFeedReader', 'TestLibrary',
    'TestMediaPlayer', 'TestMobileApp', 'TestPIM',
)
