try:
    import regex as re
except (ImportError, ModuleNotFoundError):
    import re
from .parser import Parser
from .os_fragment import OSFragment

DESKTOP_OS = {
    'AmigaOS',
    'IBM',
    'GNU/Linux',
    'Mac',
    'Unix',
    'Windows',
    'BeOS',
    'Chrome OS',
}

OPERATING_SYSTEMS = {
    'AIX': 'AIX',
    'AND': 'Android',
    'AMG': 'AmigaOS',
    'ATV': 'Apple TV',
    'ARL': 'Arch Linux',
    'BTR': 'BackTrack',
    'SBA': 'Bada',
    'BEO': 'BeOS',
    'BLB': 'BlackBerry OS',
    'QNX': 'BlackBerry Tablet OS',
    'BMP': 'Brew',
    'CES': 'CentOS',
    'COS': 'Chrome OS',
    'CYN': 'CyanogenMod',
    'DEB': 'Debian',
    'DFB': 'DragonFly',
    'FED': 'Fedora',
    'FIR': 'Fire OS',
    'FOS': 'Firefox OS',
    'BSD': 'FreeBSD',
    'GNT': 'Gentoo',
    'GTV': 'Google TV',
    'HPX': 'HP-UX',
    'HAI': 'Haiku OS',
    'IRI': 'IRIX',
    'INF': 'Inferno',
    'KOS': 'KaiOS',
    'KNO': 'Knoppix',
    'KBT': 'Kubuntu',
    'LIN': 'GNU/Linux',
    'LBT': 'Lubuntu',
    'VLN': 'VectorLinux',
    'MAC': 'Mac',
    'MAE': 'Maemo',
    'MDR': 'Mandriva',
    'SMG': 'MeeGo',
    'MCD': 'MocorDroid',
    'MIN': 'Mint',
    'MLD': 'MildWild',
    'MOR': 'MorphOS',
    'NBS': 'NetBSD',
    'MTK': 'MTK / Nucleus',
    'WII': 'Nintendo',
    'NDS': 'Nintendo Mobile',
    'OS2': 'OS/2',
    'T64': 'OSF1',
    'OBS': 'OpenBSD',
    'PSP': 'PlayStation Portable',
    'PS3': 'PlayStation',
    'RHT': 'Red Hat',
    'ROS': 'RISC OS',
    'REM': 'Remix OS',
    'RZD': 'RazoDroiD',
    'SAB': 'Sabayon',
    'SSE': 'SUSE',
    'SAF': 'Sailfish OS',
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
    'UBT': 'Ubuntu',
    'WTV': 'WebTV',
    'WIN': 'Windows',
    'WCE': 'Windows CE',
    'WMO': 'Windows Mobile',
    'WPH': 'Windows Phone',
    'WRT': 'Windows RT',
    'XBX': 'Xbox',
    'XBT': 'Xubuntu',
    'YNS': 'YunOs',
    'IOS': 'iOS',
    'POS': 'palmOS',
    'WOS': 'webOS',
    'WIO': 'Windows IoT',
    'UNK': 'Unknown',
}

# flip Abbrev / OS for fast membership testing
OS_TO_ABBREV = {os.lower(): abbrev for abbrev, os in OPERATING_SYSTEMS.items()}

OS_FAMILIES = {
    'Android': [
        'AND',
        'CYN',
        'REM',
        'RZD',
        'MLD',
        'MCD',
        'YNS',
        'FIR',
    ],
    'AmigaOS': ['AMG', 'MOR'],
    'Apple TV': ['ATV'],
    'BlackBerry': ['BLB', 'QNX'],
    'Brew': ['BMP'],
    'BeOS': ['BEO', 'HAI'],
    'Chrome OS': ['COS'],
    'Firefox OS': ['FOS', 'KOS'],
    'Gaming Console': ['WII', 'PS3'],
    'Google TV': ['GTV'],
    'IBM': ['OS2'],
    'iOS': ['IOS'],
    'RISC OS': ['ROS'],
    'GNU/Linux': [
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
    ],
    'Mac': ['MAC'],
    'Mobile Gaming Console': ['PSP', 'NDS', 'XBX'],
    'Real-time OS': ['MTK', 'TDX'],
    'Other Mobile': ['WOS', 'POS', 'SBA', 'TIZ', 'SMG', 'MAE'],
    'Symbian': ['SYM', 'SYS', 'SY3', 'S60', 'S40'],
    'Unix': [
        'SOS',
        'AIX',
        'HPX',
        'BSD',
        'NBS',
        'OBS',
        'DFB',
        'SYL',
        'IRI',
        'T64',
        'INF',
    ],
    'WebTV': ['WTV'],
    'Windows': ['WIN'],
    'Windows IoT': ['WIO'],
    'Windows Mobile': ['WPH', 'WMO', 'WCE', 'WRT'],
    'Unknown': ['UNK'],
}

FAMILY_FROM_OS = {}
for os, families in OS_FAMILIES.items():
    for family in families:
        FAMILY_FROM_OS[family] = os


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

    ARM_REGEX = re.compile(r'arm', re.IGNORECASE)
    WINDOWS_REGEX = re.compile(r'WOW64|x64|win64|amd64|x86_64', re.IGNORECASE)
    x86_REGEX = re.compile(r'i[0-9]86|i86pc', re.IGNORECASE)

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
        if self._check_regex(self.ARM_REGEX):
            return 'ARM'
        if self._check_regex(self.WINDOWS_REGEX):
            return 'x64'
        if self._check_regex(self.x86_REGEX):
            return 'x86'
        return ''

    def _parse(self):
        super()._parse()
        if not self.ua_data:
            OSFragment(self.user_agent, self.ua_hash, self.ua_spaceless).parse()
        return self.ua_data or {}

    def set_details(self) -> None:
        super().set_details()
        if self.ua_data:
            abbreviation = self.OS_TO_ABBREV.get(self.ua_data['name'].lower(), self.UNKNOWN)
            self.ua_data.update({
                # Overwrite name for capitalization.
                # insensitive regex match preserves original casing
                'name': self.OPERATING_SYSTEMS.get(abbreviation),
                'short_name': abbreviation,
                'family': self.FAMILY_FROM_OS.get(abbreviation),
                'platform': self.platform(),
            })


__all__ = (
    'DESKTOP_OS',
    'OS',
    'OPERATING_SYSTEMS',
    'OS_FAMILIES',
)
