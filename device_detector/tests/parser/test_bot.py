from ..base import ParserBaseTest
from ...parser import Bot


class TestBot(ParserBaseTest):

    def test_get_info_from_ua_bot(self):
        ua = 'Googlebot/2.1 (http://www.googlebot.com/bot.html)'
        bot = Bot(ua=ua, client_hints=None)
        expected = {
            'name': 'Googlebot',
            'category': 'Search bot',
            'url': 'https://developers.google.com/search/docs/crawling-indexing/overview-google-crawlers',
            'producer': {
                'name': 'Google Inc.',
                'url': 'https://www.google.com/',
            },
            'version': '',
        }
        bot = bot.parse()
        bot.ua_data.pop('type', None)
        self.assertDictEqual(expected, bot.ua_data)

    def test_parse_no_bot(self):
        ua = 'Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1; SV1; SE 2.x)'
        bot = Bot(ua=ua, client_hints=None)
        bot.parse()
        self.assertEqual(bot.ua_data, {})


__all__ = [
    'TestBot',
]
