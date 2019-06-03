try:
    import regex as re
except (ImportError, ModuleNotFoundError):
    import re
from . import BaseClientParser
from ...settings import BOUNDED_REGEX

AVAILABLE_ENGINES = {
    'WebKit',
    'Blink',
    'Trident',
    'Text-based',
    'Dillo',
    'iCab',
    'Elektra',
    'Presto',
    'Gecko',
    'KHTML',
    'NetFront',
    'Edge',
    'NetSurf',
}
AVAILABLE_ENGINES_LOWER_CASE = {engine.lower(): engine for engine in AVAILABLE_ENGINES}

AVAILABLE_BROWSERS = {
    '36': '360 Phone Browser',
    '3B': '360 Browser',
    'AA': 'Avant Browser',
    'AB': 'ABrowse',
    'AF': 'ANT Fresco',
    'AG': 'ANTGalio',
    'AL': 'Aloha Browser',
    'AM': 'Amaya',
    'AO': 'Amigo',
    'AN': 'Android Browser',
    'AD': 'AOL Shield',
    'AR': 'Arora',
    'AV': 'Amiga Voyager',
    'AW': 'Amiga Aweb',
    'AS': 'Avast Secure Browser',
    'AZ': 'Avast SafeZone',
    'AT': 'Atomic Web Browser',
    'BA': 'Beaker Browser',
    'BB': 'BlackBerry Browser',
    'BD': 'Baidu Browser',
    'BS': 'Baidu Spark',
    'BE': 'Beonex',
    'BJ': 'Bunjalloo',
    'BL': 'B-Line',
    'BR': 'Brave',
    'BK': 'BriskBard',
    'BX': 'BrowseX',
    'CA': 'Camino',
    'CC': 'Coc Coc',
    'CD': 'Comodo Dragon',
    'C1': 'Coast',
    'CX': 'Charon',
    'CF': 'Chrome Frame',
    'HC': 'Headless Chrome',
    'CH': 'Chrome',
    'CI': 'Chrome Mobile iOS',
    'CK': 'Conkeror',
    'CM': 'Chrome Mobile',
    'CN': 'CoolNovo',
    'CO': 'CometBird',
    'CP': 'ChromePlus',
    'CR': 'Chromium',
    'CY': 'Cyberfox',
    'CS': 'Cheshire',
    'CU': 'Cunaguaro',
    'DB': 'dbrowser',
    'DE': 'Deepnet Explorer',
    'DF': 'Dolphin',
    'DO': 'Dorado',
    'DL': 'Dooble',
    'DI': 'Dillo',
    'EI': 'Epic',
    'EL': 'Elinks',
    'EB': 'Element Browser',
    'EP': 'GNOME Web',
    'ES': 'Espial TV Browser',
    'FB': 'Firebird',
    'FD': 'Fluid',
    'FE': 'Fennec',
    'FF': 'Firefox',
    'FK': 'Firefox Focus',
    'FL': 'Flock',
    'FM': 'Firefox Mobile',
    'FW': 'Fireweb',
    'FN': 'Fireweb Navigator',
    'GA': 'Galeon',
    'GE': 'Google Earth',
    'HJ': 'HotJava',
    'IA': 'Iceape',
    'IB': 'IBrowse',
    'IC': 'iCab',
    'I2': 'iCab Mobile',
    'I1': 'Iridium',
    'ID': 'IceDragon',
    'IV': 'Isivioo',
    'IW': 'Iceweasel',
    'IE': 'Internet Explorer',
    'IM': 'IE Mobile',
    'IR': 'Iron',
    'JS': 'Jasmine',
    'JI': 'Jig Browser',
    'KI': 'Kindle Browser',
    'KM': 'K-meleon',
    'KO': 'Konqueror',
    'KP': 'Kapiko',
    'KY': 'Kylo',
    'KZ': 'Kazehakase',
    'LB': 'Liebao',
    'LG': 'LG Browser',
    'LI': 'Links',
    'LU': 'LuaKit',
    'LS': 'Lunascape',
    'LX': 'Lynx',
    'MB': 'MicroB',
    'MC': 'NCSA Mosaic',
    'ME': 'Mercury',
    'MF': 'Mobile Safari',
    'MI': 'Midori',
    'MU': 'MIUI Browser',
    'MS': 'Mobile Silk',
    'MX': 'Maxthon',
    'NB': 'Nokia Browser',
    'NO': 'Nokia OSS Browser',
    'NV': 'Nokia Ovi Browser',
    'NE': 'NetSurf',
    'NF': 'NetFront',
    'NL': 'NetFront Life',
    'NP': 'NetPositive',
    'NS': 'Netscape',
    'NT': 'NTENT Browser',
    'OB': 'Obigo',
    'OD': 'Odyssey Web Browser',
    'OF': 'Off By One',
    'OE': 'ONE Browser',
    'OI': 'Opera Mini',
    'OM': 'Opera Mobile',
    'OP': 'Opera',
    'ON': 'Opera Next',
    'OO': 'Opera Touch',
    'OR': 'Oregano',
    'OV': 'Openwave Mobile Browser',
    'OW': 'OmniWeb',
    'OT': 'Otter Browser',
    'PL': 'Palm Blazer',
    'PM': 'Pale Moon',
    'PP': 'Oppo Browser',
    'PR': 'Palm Pre',
    'PU': 'Puffin',
    'PW': 'Palm WebPro',
    'PA': 'Palmscape',
    'PX': 'Phoenix',
    'PO': 'Polaris',
    'PT': 'Polarity',
    'PS': 'Microsoft Edge',
    'QQ': 'QQ Browser',
    'QT': 'Qutebrowser',
    'QZ': 'QupZilla',
    'QM': 'Qwant Mobile',
    'RK': 'Rekonq',
    'RM': 'RockMelt',
    'SB': 'Samsung Browser',
    'SA': 'Sailfish Browser',
    'SC': 'SEMC-Browser',
    'SE': 'Sogou Explorer',
    'SF': 'Safari',
    'SH': 'Shiira',
    'SK': 'Skyfire',
    'SS': 'Seraphic Sraf',
    'SL': 'Sleipnir',
    'SM': 'SeaMonkey',
    'SN': 'Snowshoe',
    'SR': 'Sunrise',
    'SP': 'SuperBird',
    'ST': 'Streamy',
    'SX': 'Swiftfox',
    'TF': 'TenFourFox',
    'TB': 'Tenta Browser',
    'TZ': 'Tizen Browser',
    'TS': 'TweakStyle',
    'UC': 'UC Browser',
    'VI': 'Vivaldi',
    'VB': 'Vision Mobile Browser',
    'WE': 'WebPositive',
    'WF': 'Waterfox',
    'WO': 'wOSBrowser',
    'WT': 'WeTab Browser',
    'YA': 'Yandex Browser',
    'XI': 'Xiino'
}

# flip Abbrev / Brand for fast membership testing
BROWSER_TO_ABBREV = {browser.lower(): abbrev for abbrev, browser in AVAILABLE_BROWSERS.items()}

BROWSER_FAMILIES = {
    'Android Browser': ('AN', 'MU'),
    'BlackBerry Browser': ('BB',),
    'Baidu': ('BD', 'BS'),
    'Amiga': ('AV', 'AW'),
    'Chrome': (
        'AS',
        'AZ',
        'BA',
        'CH',
        'BR',
        'CC',
        'CD',
        'CM',
        'CI',
        'CF',
        'CN',
        'CR',
        'CP',
        'IR',
        'RM',
        'AO',
        'TB',
        'TS',
        'VI',
        'PT',
        'AD',
    ),
    'Firefox': (
        'FF',
        'FE',
        'FM',
        'SX',
        'FB',
        'PX',
        'MB',
        'EI',
        'WF',
        'CU',
        'TF',
        'QM',
    ),
    'Internet Explorer': ('IE', 'IM', 'PS'),
    'Konqueror': ('KO',),
    'NetFront': ('NF',),
    'NetSurf': ('NE',),
    'Nokia Browser': ('NB', 'NO', 'NV', 'DO'),
    'Opera': ('OP', 'OM', 'OI', 'ON'),
    'Safari': ('SF', 'MF'),
    'Sailfish Browser': ('SA',),
}

MOBILE_ONLY_BROWSERS = {
    '36',
    'PU',
    'SK',
    'MF',
    'OI',
    'OM',
    'DB',
    'ST',
    'BL',
    'IV',
    'FM',
    'C1',
    'AL',
    'SA',
}

# Fast membership testing
BROWSER_FAMILIES_LOWER = {browser.lower() for browser in BROWSER_FAMILIES.keys()}

# Crufty name/version prefixes too generic to be meaningful Client names
# iOS/12.1, CFNetwork/975.0.3, Android/7.0
CRUFT_NAMES = {
    'alamofire',
    'applewebkit',
    'carrier',
    'cfnetwork',
    'configuration',
    'darwin',
    'dalvik',
    'mozilla',
    'mobile',
    'ios',
    'android',
    'iphone',
    'okhttp',
    'profile',
    'symbian',
    'urbanairshiplib',
    'urbanairshiplib-android',
}

# When parsing UA strings generically, multiple name/version pairs may be found.
# Ignore the uninteresting ones
# Mozilla/5.0 (Symbian/3; Series60/5.2 NokiaN8-00/014.002; Profile/MIDP-2.1 Configuration/CLDC-1.1; en-us) AppleWebKit/525 (KHTML, like Gecko) Version/3.0 BrowserNG/7.2.6.4 3gpp-gba
SKIP_PREFIXES = set(AVAILABLE_ENGINES_LOWER_CASE.keys()) & BROWSER_FAMILIES_LOWER & CRUFT_NAMES


class EngineVersion:

    def __init__(self, user_agent):
        self.user_agent = user_agent

    def parse(self, engine) -> str:
        if not engine:
            return ''

        regex = r"{engine}\s*\/?\s*((?=\d+\.\d)\d+[.\d]*|\d{{1,7}}(?=(?:\D|$)))".format(
            engine=engine
        )
        regex = BOUNDED_REGEX.format(regex)
        match = re.search(regex, self.user_agent, re.IGNORECASE)
        if match:
            engine_version = self.user_agent[match.start():match.end()]
            try:
                return engine_version.split('/')[1]
            except IndexError:
                pass

        return ''


class Engine(BaseClientParser):

    AVAILABLE_ENGINES = AVAILABLE_ENGINES

    fixture_files = [
        'upstream/client/browser_engine.yml',
    ]

    def _parse(self):
        super()._parse()
        if 'name' in self.ua_data:
            self.ua_data['engine_version'] = EngineVersion(
                self.user_agent,
            ).parse(
                engine=self.ua_data['name'],
            )


class Browser(BaseClientParser):

    fixture_files = [
        'local/client/browsers.yml',
        'upstream/client/browsers.yml',
    ]

    AVAILABLE_ENGINES = AVAILABLE_ENGINES
    AVAILABLE_BROWSERS = AVAILABLE_BROWSERS
    BROWSER_TO_ABBREV = BROWSER_TO_ABBREV
    BROWSER_FAMILIES = BROWSER_FAMILIES
    MOBILE_ONLY_BROWSERS = MOBILE_ONLY_BROWSERS

    def set_details(self):
        super().set_details()
        if self.ua_data:
            browser = self.ua_data.get('name', '')
            self.ua_data.update({
                'short_name': self.BROWSER_TO_ABBREV.get(browser.lower(), browser),
            })

            if 'engine' not in self.ua_data:
                self.ua_data['engine'] = Engine(
                    self.user_agent,
                    self.ua_hash,
                    self.ua_spaceless,
                ).parse().ua_data

    def short_name(self) -> str:
        return self.ua_data.get('short_name', None)

    def engine(self):
        if not self.ua_data.get('engine', ''):
            return ''
        if 'default' in self.ua_data['engine']:
            return self.ua_data['engine']['default']
        return self.ua_data['engine']['name']

    def is_mobile_only(self):
        return self.short_name() in self.MOBILE_ONLY_BROWSERS


__all__ = (
    'Browser',
    'Engine',
    'AVAILABLE_ENGINES',
    'AVAILABLE_BROWSERS',
    'BROWSER_FAMILIES',
    'CRUFT_NAMES',
    'MOBILE_ONLY_BROWSERS',
    'SKIP_PREFIXES',
)
