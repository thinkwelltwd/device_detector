import unittest

from ...parser.key_value_pairs import key_value_pairs


class TestKeyValuePairs(unittest.TestCase):

    def test_trailing_key_space_version(self):
        ua = 'Mozilla/5.0 (Linux; Android 8.0.0; SM-A530W Build/R16NW; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/73.0.3683.90 Mobile Safari/537.36 Android SermonAudio.com 1.9.8'

    def test_2(self):
        ua = 'YouCam Fun/22261949 (iPhone; iOS 12.0.1; Scale/2.00)'
        self.assertListEqual(
            key_value_pairs(ua),
            [('youcamfun', 'YouCam Fun', '22261949')],
        )

    def test_3(self):
        ua = 'Aurora HDR 2018/1.1.2 Sparkle/1.13.1'
        self.assertListEqual(
            key_value_pairs(ua),
            [('aurorahdr2018', 'Aurora HDR 2018', '1.1.2')],
        )

    def test_4(self):
        ua = 'libreoffice 5.4.3.2 (92a7159f7e4af62137622921e809f8546db437e5; windows; x86;)'
        self.assertListEqual(
            key_value_pairs(ua),
            [('libreoffice', 'libreoffice', '5.4.3.2')],
        )

    def test_5(self):
        ua = 'Microsoft Office Access 2013 (15.0.4693) Windows NT 6.2'
        self.assertListEqual(
            key_value_pairs(ua),
            [('microsoftofficeaccess', 'Microsoft Office Access', '2013')],
        )

    def test_with_url1(self):
        ua = 'DigiCal (v1.8.2b; http://digibites.nl/digical)'
        self.assertListEqual(
            key_value_pairs(ua),
            [('digical', 'DigiCal', '1.8.2')],
        )

    def test_with_url2(self):
        ua = 'Mozilla/5.0 (Stellarium Bright Novae Plugin 0.1.3; http://stellarium.org/)'
        self.assertListEqual(
            key_value_pairs(ua),
            [('stellariumbrightnovaeplugin', 'Stellarium Bright Novae Plugin', '0.1.3')],
        )

    def test_6(self):
        ua = 'The Economist on iPad NA/69 CFNetwork/893.14.2 Darwin/17.3.0'
        self.assertListEqual(
            key_value_pairs(ua),
            [('theeconomistonipadna', 'The Economist on iPad NA', '69')],
        )

    def test_7(self):
        ua = 'The Columbia Bank, MD/5.11.0.42 BundleID/com.intuit.mobilebanking01368 BundleDeviceFamily/iPhone,iPad (iPhone; iPhone11,2; iPhone XS; iOS 12.1.4)'
        self.assertListEqual(
            key_value_pairs(ua),
            [('thecolumbiabank,md', 'The Columbia Bank, MD', '5.11.0.42'), ('bundleid', 'BundleID', 'com.intuit.mobilebanking01368'), ('bundledevicefamily', 'BundleDeviceFamily', 'iPhone')],
        )

    def test_8(self):
        ua = 'Podbean/iOS (http://podbean.com) 5.0 - ba7575612c9a5554c0b8f5ffc378d1c7'
        self.assertListEqual(
            key_value_pairs(ua),
            [('podbean', 'Podbean', 'iOS')],
        )

    def test_9(self):
        ua = 'wsdl2objc iPhone SermonAudio.com 4.4.5'
        self.assertListEqual(
            key_value_pairs(ua),
            [('wsdl2objciphonesermonaudio.com', 'wsdl2objc iPhone SermonAudio.com', '4.4.5')],
        )

    def test_10(self):
        ua = 'AAM 1.1 rv:1.0 (iPhone; iOS 12.0; en_US)'
        self.assertListEqual(
            key_value_pairs(ua),
            [('aam', 'AAM', '1.1')],
        )

    def test_11(self):
        ua = 'Microsoft URL Control - 6.01.9782'
        self.assertListEqual(
            key_value_pairs(ua),
            [('microsofturlcontrol', 'Microsoft URL Control', '6.01.9782')],
        )

    def test_12(self):
        ua = '1.0,win/10.0.16299,AV/17.1.2286,avl/devcontrol/17.1.3394.0,ffl'
        self.assertListEqual(
            key_value_pairs(ua),
            [('av', 'AV', '17.1.2286'), ('avl', 'avl', 'devcontrol')],
        )

    def test_13(self):
        ua = 'ArcGISiOS-10.2.5/10.3.2/iPad6,12'
        self.assertListEqual(
            key_value_pairs(ua),
            [('arcgisios-10.2.5', 'ArcGISiOS-10.2.5', '10.3.2')],
        )

    def test_is_browser_nothing_interesting1(self):
        ua = 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/46.0.2486.0 safari/537.36 edge/13.10586 edge 13.0'
        self.assertListEqual(
            key_value_pairs(ua),
            [],
        )

    def test_is_browser_nothing_interesting2(self):
        ua = 'Safari/14607.1.39 CFNetwork/978.0.6 Darwin/18.5.0 (x86_64)'
        self.assertListEqual(
            key_value_pairs(ua),
            [],
        )

    def test_is_browser_nothing_interesting3(self):
        ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.88 Safari/537.36 Vivaldi/2.4.1488.35'
        self.assertListEqual(
            key_value_pairs(ua),
            [],
        )

    def test_is_browser_nothing_interesting4(self):
        ua = 'Vivaldi/2.0.1309.37 WinSparkle/0.5.2 (Win64)'
        self.assertListEqual(
            key_value_pairs(ua),
            [],
        )

    def test_is_browser_nothing_interesting5(self):
        ua = 'Opera/9.62 (J2ME/MIDP; Opera Mini/5.1.37933421/28.62; U; en) Presto/2.521.26 Version/11.521'
        self.assertListEqual(
            key_value_pairs(ua),
            [('version', 'Version', '11.521')],
        )

    def test_is_browser_nothing_interesting6(self):
        ua = 'Opera/9.62 (Android 4.1.2; Linux; Opera Mobi/ADR-25672775) Presto/2.520.13 Version/12.520'
        self.assertListEqual(
            key_value_pairs(ua),
            [('version', 'Version', '12.520')],
        )

