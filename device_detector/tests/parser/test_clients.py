from ..base import GenericParserTest, ParserBaseTest
from ...parser import (
    Browser,
    DesktopApp,
    DictUA,
    FeedReader,
    Game,
    Library,
    MediaPlayer,
    Messaging,
    MobileApp,
    P2P,
    PIM,
    NameVersionExtractor,
    VPNProxy,
    WholeNameExtractor,
)
from ...utils import ua_hash


class TestBrowser(ParserBaseTest):

    fixture_files = [
        'tests/parser/fixtures/local/client/browser.yml',
        'tests/parser/fixtures/upstream/client/browser.yml',
    ]
    fields = ('name', 'type')
    Parser = Browser


class TestDictUA(ParserBaseTest):

    fixture_files = [
        'tests/parser/fixtures/local/client/dictua.yml',
    ]
    fields = ('name', 'version', 'type')
    Parser = DictUA


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
        'tests/parser/fixtures/local/client/desktop_apps.yml',
    ]
    fields = ('name', 'type', 'version')
    Parser = DesktopApp


class TestVPNProxy(ParserBaseTest):

    fixture_files = [
        'tests/parser/fixtures/local/client/vpnproxy.yml',
    ]
    fields = ('name', 'type', 'version')
    Parser = VPNProxy


class TestNameVersionExtractor(ParserBaseTest):

    fixture_files = [
        'tests/parser/fixtures/local/client/extractor_name_version.yml',
    ]
    fields = ('name', 'type', 'version')
    Parser = NameVersionExtractor
    skipped = (
        '$(PRODUCT_NAME)/4839 CFNetwork/894 Darwin/17.4.0',
        'MotionXGPSFull24.2b5063R-iOS12.0-iPhone7,2',
        '1530819907iOSv1.6.5',
        'ISUA11.00MP',
    )


class TestWholeNameExtractor(GenericParserTest):

    fixture_files = [
        'tests/parser/fixtures/local/client/extractor_whole_name.yml',
    ]
    fields = ('name', 'type', 'version')
    Parser = WholeNameExtractor
    skipped = [
        '646E514C51BFF23DBBB5B9487F142670_5_5.10.228257.2253_1_0',
    ]


# class TestNoNameExtracted(ParserBaseTest):
#
#     fixture_files = [
#         'tests/parser/fixtures/local/client/extractor_no_name.yml',
#     ]
#
#     def test_parsing(self):
#         fixtures = self.load_fixtures()
#         fields = ('name', 'version')
#         extractors = (WholeNameExtractor, NameVersionExtractor)
#
#         for fixture in fixtures:
#             ua = fixture.pop('user_agent')
#
#             for extractor in extractors:
#                 parsed = extractor(ua, ua_hash(ua), ua.lower().replace(' ', '')).parse()
#
#                 for field in fields:
#                     self.assertNotIn(field, parsed.ua_data)

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
    'TestNameVersionExtractor',
    'TestWholeNameExtractor',
    # 'TestNoNameExtracted',
)
