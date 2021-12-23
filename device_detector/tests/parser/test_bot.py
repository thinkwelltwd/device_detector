from ..base import ParserBaseTest
from ...parser import Bot
from ...utils import ua_hash


class TestBot(ParserBaseTest):

    def test_get_info_from_ua_bot(self):
        ua = 'Googlebot/2.1 (http://www.googlebot.com/bot.html)'
        spaceless = ua.lower().replace(' ', '')
        bot = Bot(
            ua=ua,
            ua_hash=ua_hash(ua),
            ua_spaceless=spaceless,
            version_truncation=self.VERSION_TRUNCATION,
        )
        expected = {
            'name': 'Googlebot',
            'category': 'Search bot',
            'url': 'http://www.google.com/bot.html',
            'producer': {
                'name': 'Google Inc.',
                'url': 'http://www.google.com',
            },
            'model': '',
            'version': '',
        }
        bot = bot.parse()
        bot.ua_data.pop('type', None)
        self.assertDictEqual(expected, bot.ua_data)

    def test_parse_no_bot(self):
        ua = 'Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1; SV1; SE 2.x)'
        spaceless = ua.lower().replace(' ', '')
        bot = Bot(
            ua=ua,
            ua_hash=ua_hash(ua),
            ua_spaceless=spaceless,
            version_truncation=self.VERSION_TRUNCATION,
        )
        bot.parse()
        self.assertEqual(bot.ua_data, {})


__all__ = [
    'TestBot',
]
