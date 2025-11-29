from urllib.parse import unquote
from ..base import ParserBaseTest
from ...parser import OS
from ...device_detector import DeviceDetector
from ...parser.client_hints import ClientHints


class TestClientHints(ParserBaseTest):

    fixture_files = [
        'tests/fixtures/upstream/clienthints.yml',
    ]

    def test_parsing(self):
        for fixture in self.load_fixtures():
            self.user_agent = unquote(fixture['user_agent'])
            parsed = DeviceDetector(user_agent=self.user_agent, headers=fixture['headers']).parse()
            parsed_data = parsed.all_details

            # Skip checking the "device" section since
            # we're not ss interested in device specifics.
            for section in ('os', 'client'):
                expected = fixture.get(section) or {}
                extracted = parsed_data.get(section) or {}

                for k, expected_value in expected.items():
                    if k in ('engine', 'version', 'engine_version'):
                        continue

                    extracted_value = None if extracted.get(k) == 'Unknown' else extracted.get(k)

                    # Consider names valid if they vary only by spacing
                    if k == 'name' and extracted_value:
                        if (
                            extracted_value != expected_value
                            and extracted_value.replace(' ', '') == expected_value.replace(' ', '')
                        ):
                            continue

                    self.assertEqual(
                        extracted_value,
                        extracted_value,
                        msg=f'Section: {section!r}. '
                            f'Key: {k!r}. '
                            f'Expected: {expected_value!r}. '
                            f'Actual: {extracted_value!r}. '
                            f'User agent: {self.user_agent!r}',
                    )

    def test_headers(self):
        headers = {
            'sec-ch-ua' : '"Opera";v="83", " Not;A Brand";v="99", "Chromium";v="98"',
            'sec-ch-ua-mobile' : '?0',
            'sec-ch-ua-platform' : 'Windows',
            'sec-ch-ua-platform-version': '14.0.0',
        }
        ch = ClientHints.new(headers)

        self.assertFalse(ch.is_mobile())
        self.assertTrue(ch.is_desktop())
        self.assertEqual(ch.platform, 'Windows')
        self.assertEqual(ch.platform_version, '14.0.0')

        ch_map = {
            'Opera': '83',
            'Chromium': '98',
        }
        self.assertDictEqual(ch_map, ch.client_hints_map)

    def test_headers_http(self):
        headers = {
            'HTTP_SEC_CH_UA_FULL_VERSION_LIST' : '" Not A;Brand";v="99.0.0.0", "Chromium";v="98.0.4758.82", "Opera";v="98.0.4758.82"',
            'HTTP_SEC_CH_UA': '" Not A;Brand";v="99", "Chromium";v="98", "Opera";v="84"',
            'HTTP_SEC_CH_UA_MOBILE' : '?0',
            'HTTP_SEC_CH_UA_MODEL' : 'DN2103',
            'HTTP_SEC_CH_UA_PLATFORM' : 'Ubuntu',
            'HTTP_SEC_CH_UA_PLATFORM_VERSION': '3.7',
            'HTTP_SEC_CH_UA_FULL_VERSION': '98.0.14335.105',
        }
        ch = ClientHints.new(headers)

        self.assertFalse(ch.is_mobile())
        self.assertTrue(ch.is_desktop())
        self.assertEqual(ch.platform, 'Ubuntu')
        self.assertEqual(ch.platform_version, '3.7')
        self.assertEqual(ch.model, 'DN2103')

        ch_map = {
            'Opera': '98.0.4758.82',
            'Chromium': '98.0.4758.82',
        }
        self.assertDictEqual(ch_map, ch.client_hints_map)

    def test_os(self):

        fixtures = [
            {
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36 OPR/83.0.4254.27',
                'headers': {
                    'sec-ch-ua': '"Opera";v="83", " Not;A Brand";v="99", "Chromium";v="98"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': 'Windows',
                    'sec-ch-ua-platform-version': '14.0.0',
                },
                'os': {
                    'name': 'Windows',
                    'short_name': 'WIN',
                    'version': '11',
                    'family': 'Windows',
                },
            },
            {
                'user_agent': '',
                'headers': {
                    'Sec-CH-UA': '"AvastSecureBrowser";v="6.6.0", " Not A;Brand";v="99.0.0.0", "Chromium";v="98.0.4758.101"',
                    'Sec-CH-UA-Platform': 'Android',
                    'Sec-CH-UA-Mobile': '?1',
                    'Sec-CH-UA-Full-Version': '6.6.0',
                    'Sec-CH-UA-Platform-Version': '11',
                    'Sec-CH-UA-Arch': '[arm64-v8a, armeabi-v7a, armeabi]',
                    'Sec-CH-Prefers-Color-Scheme': 'light',
                },
                'os': {
                    'name': 'Android',
                    'version': '11',
                    'platform': 'ARM',
                },
            },
        ]

        for fixture in fixtures:
            self.user_agent = unquote(fixture.pop('user_agent'))
            expect = fixture['os']

            ch = ClientHints.new(fixture['headers'])
            spaceless = self.user_agent.lower().replace(' ', '')
            parsed = OS(self.user_agent, spaceless, ch).parse()

            data = parsed.ua_data

            for key, value in expect.items():
                self.assertEqual(
                    str(expect[key]),
                    str(data.get(key)),
                    field=key,
                )
