from ..base import ParserBaseTest
from ...parser import Bot


class TestBot(ParserBaseTest):

    def test_get_info_from_ua_bot(self):
        bot = Bot('Googlebot/2.1 (http://www.googlebot.com/bot.html)')
        expected = {
            'name': 'Googlebot',
            'category': 'Search bot',
            'url': 'http://www.google.com/bot.html',
            'producer': {
                'name': 'Google Inc.',
                'url': 'http://www.google.com',
            }
        }
        bot = bot.parse()
        bot.ua_data.pop('type', None)
        self.assertDictEqual(expected, bot.ua_data)

    def test_parse_no_bot(self):
        bot = Bot('Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1; SV1; SE 2.x)')
        bot.parse()
        self.assertEqual(bot.ua_data, {})


__all__ = (
    'TestBot',
)
