from .parser import Parser
from .os_fragment import OSFragment
from ..lazy_regex import RegexLazyIgnore
from .settings import normalized_name
from ..settings import BOUNDED_REGEX

WEBOS_VERSION = RegexLazyIgnore(r'WEBOS([\d\.]+)')

DESKTOP_OS = {'AmigaOS', 'IBM', 'GNU/Linux', 'Mac', 'Unix', 'Windows', 'BeOS', 'Chrome OS'}

OPERATING_SYSTEMS = {
    'AIX': 'AIX',
    'AND': 'Android',
    'AMG': 'AmigaOS',
    'ATV': 'tvOS',
    'ARL': 'Arch Linux',
    'BTR': 'BackTrack',
    'SBA': 'Bada',
    'BEO': 'BeOS',
    'BLB': 'BlackBerry OS',
    'QNX': 'BlackBerry Tablet OS',
    'BMP': 'Brew',
    'CAI': 'Caixa Mágica',
    'CES': 'CentOS',
    'COS': 'Chrome OS',
    'CYN': 'CyanogenMod',
    'DEB': 'Debian',
    'DEE': 'Deepin',
    'DFB': 'DragonFly',
    'DVK': 'DVKBuntu',
    'FED': 'Fedora',
    'FEN': 'Fenix',
    'FOS': 'Firefox OS',
    'FIR': 'Fire OS',
    'FRE': 'Freebox',
    'BSD': 'FreeBSD',
    'FYD': 'FydeOS',
    'GNT': 'Gentoo',
    'GRI': 'GridOS',
    'GTV': 'Google TV',
    'HPX': 'HP-UX',
    'HAI': 'Haiku OS',
    'IPA': 'iPadOS',
    'HAR': 'HarmonyOS',
    'HAS': 'HasCodingOS',
    'IRI': 'IRIX',
    'INF': 'Inferno',
    'JME': 'Java ME',
    'KOS': 'KaiOS',
    'KNO': 'Knoppix',
    'KBT': 'Kubuntu',
    'LIN': 'GNU/Linux',
    'LBT': 'Lubuntu',
    'LOS': 'Lumin OS',
    'VLN': 'VectorLinux',
    'MAC': 'Mac',
    'MAE': 'Maemo',
    'MAG': 'Mageia',
    'MDR': 'Mandriva',
    'SMG': 'MeeGo',
    'MCD': 'MocorDroid',
    'MIN': 'Mint',
    'MLD': 'MildWild',
    'MOR': 'MorphOS',
    'NBS': 'NetBSD',
    'MTK': 'MTK / Nucleus',
    'MRE': 'MRE',
    'WII': 'Nintendo',
    'NDS': 'Nintendo Mobile',
    'OS2': 'OS/2',
    'T64': 'OSF1',
    'OBS': 'OpenBSD',
    'OWR': 'OpenWrt',
    'ORD': 'Ordissimo',
    'PCL': 'PCLinuxOS',
    'PSP': 'PlayStation Portable',
    'PS3': 'PlayStation',
    'RHT': 'Red Hat',
    'ROS': 'RISC OS',
    'ROK': 'Roku OS',
    'RSO': 'Rosa',
    'REM': 'Remix OS',
    'REX': 'REX',
    'RZD': 'RazoDroiD',
    'SAB': 'Sabayon',
    'SSE': 'SUSE',
    'SAF': 'Sailfish OS',
    'SEE': 'SeewoOS',
    'SLW': 'Slackware',
    'SOS': 'Solaris',
    'SYL': 'Syllable',
    'SYM': 'Symbian',
    'SYS': 'Symbian OS',
    'S40': 'Symbian OS Series 40',
    'S60': 'Symbian OS Series 60',
    'SY3': 'Symbian^3',
    'TDX': 'ThreadX',
    'TIZ': 'Tizen',
    'TOS': 'TmaxOS',
    'UBT': 'Ubuntu',
    'WAS': 'watchOS',
    'WTV': 'WebTV',
    'WHS': 'Whale OS',
    'WIN': 'Windows',
    'WCE': 'Windows CE',
    'WIO': 'Windows IoT',
    'WMO': 'Windows Mobile',
    'WPH': 'Windows Phone',
    'WRT': 'Windows RT',
    'XBX': 'Xbox',
    'XBT': 'Xubuntu',
    'YNS': 'YunOs',
    'IOS': 'iOS',
    'POS': 'palmOS',
    'WOS': 'webOS',
    'UNK': 'Unknown',
}

# flip Abbrev / OS for fast membership testing
OS_TO_ABBREV = {os.lower(): abbrev for abbrev, os in OPERATING_SYSTEMS.items()}

OS_FAMILIES = {
    'Android': [
        'AND',
        'CYN',
        'FIR',
        'REM',
        'RZD',
        'MLD',
        'MCD',
        'YNS',
        'GRI',
        'HAR',
    ],
    'AmigaOS': ('AMG', 'MOR'),
    'BlackBerry': ('BLB', 'QNX'),
    'Brew': ('BMP',),
    'BeOS': ('BEO', 'HAI'),
    'Chrome OS': ('COS', 'FYD', 'SEE'),
    'Firefox OS': ('FOS', 'KOS'),
    'Gaming Console': ('WII', 'PS3'),
    'Google TV': ('GTV',),
    'IBM': ('OS2',),
    'iOS': ('IOS', 'ATV', 'WAS', 'IPA'),
    'RISC OS': ('ROS',),
    'GNU/Linux': (
        'LIN',
        'ARL',
        'DEB',
        'KNO',
        'MIN',
        'UBT',
        'KBT',
        'XBT',
        'LBT',
        'FED',
        'RHT',
        'VLN',
        'MDR',
        'GNT',
        'SAB',
        'SLW',
        'SSE',
        'CES',
        'BTR',
        'SAF',
        'ORD',
        'TOS',
        'RSO',
        'DEE',
        'FRE',
        'MAG',
        'FEN',
        'CAI',
        'PCL',
        'HAS',
        'LOS',
        'DVK',
        'ROK',
        'OWR',
    ),
    'Mac': ('MAC',),
    'Mobile Gaming Console': ('PSP', 'NDS', 'XBX'),
    'Real-time OS': ('MTK', 'TDX', 'MRE', 'JME', 'REX'),
    'Other Mobile': ('WOS', 'POS', 'SBA', 'TIZ', 'SMG', 'MAE'),
    'Symbian': ('SYM', 'SYS', 'SY3', 'S60', 'S40'),
    'Unix': ('SOS', 'AIX', 'HPX', 'BSD', 'NBS', 'OBS', 'DFB', 'SYL', 'IRI', 'T64', 'INF'),
    'WebTV': ('WTV',),
    'Windows': ('WIN',),
    'Windows Mobile': ('WPH', 'WMO', 'WCE', 'WRT', 'WIO'),
    'Other Smart TV': ('WHS',),
    'Unknown': ('UNK',),
}

FAMILY_FROM_OS = {}
for os, families in OS_FAMILIES.items():
    for family in families:
        FAMILY_FROM_OS[family] = os

ARM_REGEX = RegexLazyIgnore(BOUNDED_REGEX.format('arm|aarch64|Apple ?TV|Watch ?OS|Watch1,[12]'))
MIPS_REGEX = RegexLazyIgnore(BOUNDED_REGEX.format('mips'))
SUPERH_REGEX = RegexLazyIgnore(BOUNDED_REGEX.format('sh4'))
WINDOWS_REGEX = RegexLazyIgnore(
    BOUNDED_REGEX.format(r'64-?bit|WOW64|(?:Intel)?x64|win64|amd64|x86_?64')
)
x86_REGEX = RegexLazyIgnore(BOUNDED_REGEX.format('.+32bit|.+win32|(?:i[0-9]|x)86|i86pc'))


class OS(Parser):

    fixture_files = [
        'local/oss.yml',
        'upstream/oss.yml',
    ]

    DESKTOP_OS = DESKTOP_OS
    OPERATING_SYSTEMS = OPERATING_SYSTEMS
    OS_TO_ABBREV = OS_TO_ABBREV
    OS_FAMILIES = OS_FAMILIES
    FAMILY_FROM_OS = FAMILY_FROM_OS

    def is_desktop(self) -> bool:
        return self.family() in self.DESKTOP_OS

    def short_name(self) -> str:
        return self.ua_data.get('short_name', '')

    def family(self) -> str:
        return self.ua_data.get('family', '')

    def is_known(self) -> bool:
        if self.short_name() == self.UNKNOWN:
            return False
        return super().is_known()

    def platform(self) -> str:
        if self._check_regex(ARM_REGEX):
            return 'ARM'
        if self._check_regex(MIPS_REGEX):
            return 'MIPS'
        if self._check_regex(SUPERH_REGEX):
            return 'SuperH'
        if self._check_regex(WINDOWS_REGEX):
            return 'x64'
        if self._check_regex(x86_REGEX):
            return 'x86'
        return ''

    def _parse(self):
        super()._parse()
        if not self.ua_data:
            OSFragment(
                self.user_agent,
                self.ua_hash,
                self.ua_spaceless,
                self.VERSION_TRUNCATION,
            ).parse()
        return self.ua_data or {}

    def set_details(self) -> None:
        super().set_details()
        if self.ua_data:
            name = normalized_name(
                self.ua_data['name'].lower(),
                self.OS_TO_ABBREV,
                self.OPERATING_SYSTEMS,
            )
            abbreviation = self.OS_TO_ABBREV.get(name.lower(), self.UNKNOWN)
            self.ua_data.update({
                'name': name,
                'short_name': abbreviation,
                'family': self.FAMILY_FROM_OS.get(abbreviation),
                'platform': self.platform(),
                'version': self.set_version(self.ua_data.get('version')),
            })

    def set_version(self, version):
        version = super().set_version(version)

        if not version:
            # Extract version from WEBOS4.5 substring
            name = self.ua_data.get('name', '')
            if name and name.lower() == 'webos':
                match = WEBOS_VERSION.search(self.user_agent)
                if match:
                    version = match.group(1)

        return version


__all__ = (
    'DESKTOP_OS',
    'OS',
    'OPERATING_SYSTEMS',
    'OS_FAMILIES',
)
