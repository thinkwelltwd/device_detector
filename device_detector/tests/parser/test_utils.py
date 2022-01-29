from unittest import TestCase

from device_detector.utils import (
    mostly_repeating_characters,
    only_numerals_and_punctuation,
    mostly_numerals,
    random_alphanumeric_string,
    uuid_like_name,
)


# -----------------------------------------------------------------------
class TestNotUUIDname(TestCase):

    def test_user_agent_like_uuid(self):
        for ua in (
                '738FAAEF-30CF',
                '6BFAD903-A5EA-4E34',
                '5FAEB6ED-AE46-4A26-BA1B',
                'ea1866cb-c89a-6d5d-89b8-afdcdb715237',
        ):
            self.assertTrue(
                uuid_like_name(ua),
                msg='%s is similar to a UUID' % ua,
            )

    def test_user_agent_not_like_uuid(self):
        for ua in (
                'Waterman-WZVN',
                'Grainger-Cats',
                'Boxcarts-8932',
        ):
            self.assertFalse(
                uuid_like_name(ua),
                msg='%s is not similar to a UUID' % ua,
            )


# -----------------------------------------------------------------------
class TestNotNumerals(TestCase):

    def test_user_agent_mostly_numerals(self):
        for ua in (
                '2349090',
                'Tx23490923v',
                '4444444444444444444444444sdfasd',
        ):
            self.assertTrue(
                mostly_numerals(ua),
                msg='%s is mostly numerical' % ua,
            )

    def test_numerical_names_spaces_allowed(self):
        """
        If a name with mostly numerals contains a space, don't reject it.
        """
        for ua in (
                'Xray 2.35.90/23.19',
                'Tesla 9-5883/2.35.90/23.19',
        ):
            self.assertFalse(
                mostly_numerals(ua),
                msg='%s is not considered mostly numerical' % ua,
            )

    def test_not_mostly_numerals_punctuation(self):
        for ua in (
                '234.90/90',
                '2-3.40/5',
                '345/90.9 45.20.4.5',
        ):
            self.assertTrue(
                only_numerals_and_punctuation(ua),
                msg='%s is only numerals and punctuation' % ua,
            )


class TestNotGibberish(TestCase):

    def test_gibberish_ua_strings(self):
        for ua in (
                'Ya0eXACkoylZb9TS9qacxCw8XxYzWWuXQAAAAA',
                'Ya0eXACkoylZb9TS9qacxCw8XxYXW0gYQAAAAA',
                '001471FmBjtgZvahkMJdcGJhhjXuuD99',
                '002261f23pRwrjIEtS1MrX0lZ4hx8N7P',
                '002353ueFfucaEDjKRbKwlpDpecxwYwC',
                'ziNICEarE9VlaPSkhDAyZrkZSpuEkIA',
                '002921Fw0cheewpv5V82uy0sQ5DLeXyC',
                '002404WQDQjvKP3nVYqAhONTZ8U3IJOq',
                '003703Z6BUGEG0SGHIGyCbPoLC4CjTMw',
                '003098zRAFF8LcClf2Db1g1WPHsFhBOh',
                'ziNICEarE9VlaPSkhDAyZrkZSpuEkIA',
                'yN6OR5feZZJLWQ7ACkTkSFVAzhhd7g',
                '005398AzsR1apMZDU3R4eKUn2Ce2YP2t',
                '019075NAmsDfAyLQwfYzrItmHUokQmg4',
                '988629DFoPiphgYXrAXFQ4PVvARYJhGo',
                '008847Zab1zwuMkakvROGNpDADGmsncM',
                '0176150ybYVbSawNcofPImqRStnzfQNd',
                '0187803xp7UeBtUytFoixmJAUgKIDDpL',
                '029212UcpIeYpvvoYWWEjuzn4UxMTOVN',
                '988629DFoPiphgYXrAXFQ4PVvARYJhGo',
                '029607qypCjEVzUvbkocrIrLXEuVIeen',
                '04511892N6RXcmAMsIHTTUxwhynHDpAe',
                '016734gFTOFOHOVwkEEJiY2EUUeSRnZu',
                '124856aRNUaoXlJaDUtZULmL44LNoIqa',
                '1116610FoLlb56WHsQCrXfDMdmzClzpd',
                '166694kNMwYcM2daaPAdkqunFhojumdS',
                'zWOjZVKqdtwb2vdv2hvWpHzUGNY',
                'D6A8DBACB0C1',
                'vVNYZaiXO9Hd5zAi',
                'W6o8uLSXW8gagZqDA',
                'zmV3SkWiLPNcSXNmhvFbQjpyk',
        ):
            self.assertTrue(
                random_alphanumeric_string(ua),
                msg='%s is random gibberish' % ua,
            )

    def test_not_gibberish_ua_strings(self):
        for ua in (
                'WeatherWeatherFoundation115F',
                'VrboTripWidgetExtension',
                'Wordswithfriends3',
                'Farmville2Countryescape',
                'yourswagfontsandquotesfree',
                'ZooskAndroid',
                'ZombodroidMemegenerator',
                'ZombieOutbreakSimulator',
                'WatercolorPaintingUniqueArt',
                'YellowPagesMessageApp',
                'ZeroiOSWidgetsExtension',
                'YouTubeUnplugged',
                'Youtube2016Oct16KI',
                'YouTubeMusicWidgetKitExtension',
                'YouTubeMusicTodayExtensionSkylark',
                'YahooWeatherNotificationServiceExtension',
                'YahooWeatherWeatherWidgetExtension',
                'YahooWeatherLiveWidget',
                'YAppNotificationServiceExtension',
                'YahooNewsWidgetExtension',
                'Volcanoes&Earthquakes',
                'MoviePosterWallpaperMaker',
                'LedWiFiDalsRGBW',
                'PoliceChase2Trucker',
                'PaperLabelMaker',
                'WorldTranslatorLite',
                'SynchronyCarCare',
                'AdobeCloudShare',
                'Americantruck2017',
                'worldtimebuddy',
                'AudioBook002',
                'simulator2018',
                'Scan2CadV10',
                'Perfect365',
                'StocksProTodayWidget',
                'bettycrockerbigbookcupcakes',
                'flytransporterairplanepilot',
                'Tube360VR',
                '3026moat',
                'goknots3d',
                'SuperBird',
                'wordcafe',
                'Vivaldi',
                'UT4Aplus',
                'CoffeeF2P',
                'zombiegun3d',
                'sniper3d',
                'TimeClockFree',
                'Volo',
                'Syncro',
                'SynkedUp',
                'simgai3d',
                'sylvaniasmart',
                'Tuunes',
                'Traffie',
                'Toyota',
                'talk',
                'tabcar',
                'Tapcart',
                'Snaptube',
                'Qlock',
                'Quickshot',
                'Roblox',
                'Scrapy',
                'Schoology',
                'Scape',
                'Scanbot',
                'Setup',
                'rampage',
                'PikLab',
                'PicLab',
                'Polyglot',
                'Popsa',
                'pamadunknbeat',
                'woodoku',
                'Wordly',
                'WeHunt',
                'Weebly',
                'weirdlaws',
                'WeDrum',
                'RackIPH',
                'Owltail',
                'Paycor',
                'PCAPro',
                'Roadie',
                'Quora',
                'ToonPackiMessage',
                'Voicy',
                'Wakie',
                'Wikibot',
                'WikiArt',
                'YumpuNews',
                'VOClock',
                'Volkswagen',
                'Wakeboard',
                'wartroops1917',
                'pic2shop',
                'zescape',
                'zipCAT',
                '100Lessons',
                'BoxCar 2.30',
                'JQSmartBand',
        ):
            self.assertFalse(
                random_alphanumeric_string(ua),
                msg='%s is not random gibberish' % ua,
            )


class TestNotRepeatingCharacters(TestCase):

    def test_mostly_repeating_characters(self):
        for ua in (
                'b888888888888888888888x888888',
                '88888888888888888888888888888',
                'PUUUUUUUUUUUUUUUUXXXXXXXXX555',
                'AKAKAKAKAKAKAKAKAKA',
        ):
            self.assertTrue(
                mostly_repeating_characters(ua),
                msg='%s is mostly repeating characters' % ua,
            )

    def test_not_mostly_repeating_characters(self):
        for ua in (
                '1island',
                'cmeaom Android Radarym',
                'AivAndroidPlayer',
                'Alaskaairlines Android',
        ):
            self.assertFalse(
                mostly_repeating_characters(ua),
                msg='%s is not mostly repeating characters' % ua,
            )
