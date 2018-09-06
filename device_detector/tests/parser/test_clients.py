from ..base import ParserBaseTest
from ...parser import (
    Browser,
    DesktopApp,
    FeedReader,
    Game,
    Library,
    MediaPlayer,
    Messaging,
    MobileApp,
    P2P,
    PIM,
    SlashedNameExtractor,
    VPNProxy,
    WholeNameExtractor
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


class TestGame(ParserBaseTest):

    fixture_files = [
        'tests/parser/fixtures/local/client/games.yml',
    ]
    fields = ('name', 'type', 'version')
    Parser = Game


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


class TestMessaging(ParserBaseTest):

    fixture_files = [
        'tests/parser/fixtures/local/client/messaging.yml',
    ]
    fields = ('name', 'type', 'version')
    Parser = Messaging


class TestMobileApp(ParserBaseTest):

    fixture_files = [
        'tests/parser/fixtures/local/client/mobile_app.yml',
        'tests/parser/fixtures/upstream/client/mobile_app.yml',
    ]
    fields = ('name', 'type', 'version')
    Parser = MobileApp


class TestP2P(ParserBaseTest):

    fixture_files = [
        'tests/parser/fixtures/local/client/p2p.yml',
    ]
    fields = ('name', 'type', 'version')
    Parser = P2P


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


class TestVPNProxy(ParserBaseTest):

    fixture_files = [
        'tests/parser/fixtures/local/client/vpnproxy.yml',
    ]
    fields = ('name', 'type', 'version')
    Parser = VPNProxy


class TestSlashedNameExtractor(ParserBaseTest):

    fixture_files = [
        'tests/parser/fixtures/local/client/slashed_name_extractor.yml'
    ]
    fields = ('name', 'type', 'version')
    Parser = SlashedNameExtractor


class TestWholeNameExtractor(ParserBaseTest):

    fixture_files = [
        'tests/parser/fixtures/local/client/whole_name_extractor.yml'
    ]
    fields = ('name', 'type', 'version')
    Parser = WholeNameExtractor


__all__ = (
    'TestBrowser',
    'TestDesktopApp',
    'TestFeedReader',
    'TestGame',
    'TestLibrary',
    'TestMediaPlayer',
    'TestMessaging',
    'TestMobileApp',
    'TestP2P',
    'TestPIM',
    'TestVPNProxy',
    'TestSlashedNameExtractor',
    'TestWholeNameExtractor'
)
