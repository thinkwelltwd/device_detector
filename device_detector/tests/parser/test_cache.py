from ..base import ParserBaseTest
from ...device_detector import DeviceDetector


class TestCache(ParserBaseTest):
    """
    Values should remain the same on multiple runs when
    the parsing on followup runs pulls from cached values.
    """

    def test_is_bot(self):
        ua = "Mozilla/5.0 (compatible; CloudFlare-AlwaysOnline/1.0; +http://www.cloudflare.com/always-online) AppleWebKit/534.34"

        first_run = DeviceDetector(ua).parse()
        self.assertTrue(first_run.is_bot())

        second_run = DeviceDetector(ua).parse()
        self.assertTrue(second_run.is_bot())

    def test_device(self):
        ua = "Mozilla/5.0 (Linux; U; Android 2.3.3; ja-jp; COOLPIX S800c Build/CP01_WW) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1"

        first_run = DeviceDetector(ua).parse()
        self.assertEqual(first_run.device_type(), 'camera')
        self.assertEqual(first_run.device_brand(), 'Nikon')

        second_run = DeviceDetector(ua).parse()
        self.assertEqual(second_run.device_type(), 'camera')
        self.assertEqual(second_run.device_brand(), 'Nikon')

    def test_client(self):
        ua = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"

        first_run = DeviceDetector(ua).parse()
        self.assertEqual(first_run.client_name(), 'Chrome')
        self.assertEqual(first_run.client_version(), '80.0.3987.162')

        second_run = DeviceDetector(ua).parse()
        self.assertEqual(second_run.client_name(), 'Chrome')
        self.assertEqual(second_run.client_version(), '80.0.3987.162')

    def test_os(self):
        ua = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:74.0) Gecko/20100101 Firefox/74.0"

        first_run = DeviceDetector(ua).parse()
        self.assertEqual(first_run.os_name(), 'Ubuntu')

        second_run = DeviceDetector(ua).parse()
        self.assertEqual(second_run.os_name(), 'Ubuntu')


__all__ = [
    'TestCache',
]
