from urllib.parse import unquote
from device_detector.parser import ClientHints
from device_detector.device_detector import lookup_user_agent
from ..base import GenericParserTest, ParserBaseTest
from ...parser import (
    AdobeCC,
    Browser,
    DesktopApp,
    DictUA,
    FeedReader,
    Library,
    MediaPlayer,
    MobileApp,
    OsUtility,
    PIM,
    NameVersionExtractor,
    WholeNameExtractor,
)


class ParserClientBase(ParserBaseTest):

    def test_parsing(self):
        if not self.Parser or not self.fields:
            return

        fixtures = self.load_fixtures()

        for fixture in fixtures:
            self.user_agent = unquote(fixture.pop('user_agent'))
            expect = fixture[self.fixture_key]
            # clear cache because fixture files may contain duplicate UAs
            lookup_user_agent.cache_clear()
            parsed = self.Parser(
                self.user_agent,
                client_hints=ClientHints.new(fixture.get('headers', {})),
            ).parse()
            data = parsed.ua_data

            for field in self.fields:
                expected = str(expect.get(field, '')).lower()
                extracted = str(data.get(field, '')).lower()

                # Consider names valid if they vary only by casing and spacing
                if field == 'name' and extracted:
                    if (
                        expected != extracted
                        and expected.replace(' ', '') == extracted.replace(' ', '')
                    ):
                        continue

                self.assertIn(
                    field,
                    data,
                    msg=f'Error parsing {self.user_agent!r}. Parsed data missing {field!r} key.'
                )
                self.assertEqual(expected, extracted, field=field)


class TestBrowser(ParserClientBase):

    fixture_files = [
        'tests/parser/fixtures/upstream/client/browser.yml',
        'tests/parser/fixtures/local/client/browser.yml',
    ]
    fields = ('name', 'type')
    Parser = Browser


class TestChrome(ParserClientBase):

    fixture_files = [
        'tests/parser/fixtures/local/client/chrome.yml',
    ]
    fields = ('name', 'type', 'version')
    Parser = Browser


class TestAdobeCC(ParserClientBase):

    fixture_files = [
        'tests/parser/fixtures/local/client/adobe_cc.yml',
    ]
    fields = ('name', 'type', 'version')
    Parser = AdobeCC


class TestDesktopApp(ParserClientBase):

    fixture_files = [
        'tests/parser/fixtures/local/client/desktop_app.yml',
    ]
    fields = ('name', 'version')
    Parser = DesktopApp


class TestDictUA(ParserClientBase):

    fixture_files = [
        'tests/parser/fixtures/local/client/dictua.yml',
    ]
    fields = ('name', 'version')
    Parser = DictUA


class TestFeedReader(ParserClientBase):

    fixture_files = [
        'tests/parser/fixtures/upstream/client/feed_reader.yml',
    ]
    fields = ('name', 'type', 'version')
    Parser = FeedReader


class TestLibrary(ParserClientBase):

    fixture_files = [
        'tests/parser/fixtures/local/client/library.yml',
        'tests/parser/fixtures/upstream/client/library.yml',
    ]
    fields = ('name', 'type', 'version')
    Parser = Library


class TestMediaPlayer(ParserClientBase):

    fixture_files = [
        'tests/parser/fixtures/upstream/client/mediaplayer.yml',
    ]
    fields = ('name', 'type', 'version')
    Parser = MediaPlayer


class TestMobileApp(ParserClientBase):

    fixture_files = [
        'tests/parser/fixtures/local/client/mobile_app.yml',
        'tests/parser/fixtures/upstream/client/mobile_app.yml',
    ]
    fields = ('name', 'type', 'version')
    Parser = MobileApp


class TestOsUtility(ParserClientBase):

    fixture_files = [
        'tests/parser/fixtures/local/client/osutility.yml',
    ]
    fields = ('name', 'type', 'version')
    Parser = OsUtility


class TestPIM(ParserClientBase):

    fixture_files = [
        'tests/parser/fixtures/local/client/pim.yml',
        'tests/parser/fixtures/upstream/client/pim.yml',
    ]
    fields = ('name', 'type', 'version')
    Parser = PIM


class TestNameVersionExtractor(ParserClientBase):

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

    def test_ua_with_no_interesting_keys(self):
        user_agents = (
            'Chrome/136.0.7103.42 iPhone/18.6.2 hw/iPhone14_5',
            'Chrome/138.0.7204.156 iPad/18.6.2 hw/iPad14_',
        )
        for ua in user_agents:
            wn = WholeNameExtractor(ua, client_hints=None).parse()
            self.assertEqual(wn.name(), '')


__all__ = (
    'TestBrowser',
    'TestFeedReader',
    'TestLibrary',
    'TestMediaPlayer',
    'TestMobileApp',
    'TestPIM',
    'TestNameVersionExtractor',
    'TestWholeNameExtractor',
)
