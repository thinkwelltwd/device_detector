from .parser import Parser
from .os_fragment import OSFragment
from ..lazy_regex import RegexLazyIgnore
from .settings import (
    normalized_name,
    CHROME_OS_MODELS,
    DESKTOP_OS,
    OPERATING_SYSTEMS,
    OS_TO_ABBREV,
    OS_FAMILIES,
    FAMILY_FROM_OS,
    ANDROID_APPS,
    FIREOS_VERSION_MAPPING,
    LINEAGEOS_VERSION_MAPPING,
)
from ..settings import BOUNDED_REGEX

WEBOS_VERSION = RegexLazyIgnore(r'WEBOS([\d\.]+)')

ARM_REGEX = RegexLazyIgnore(
    BOUNDED_REGEX.format(r'arm[ _;)ev]|.*arm$|.*arm64|aarch64|Apple ?TV|Watch ?OS|Watch1,[12]')
)
LOONGARCH_REGEX = RegexLazyIgnore(BOUNDED_REGEX.format('loongarch64'))
MIPS_REGEX = RegexLazyIgnore(BOUNDED_REGEX.format('mips'))
SPARK_REGEX = RegexLazyIgnore(BOUNDED_REGEX.format('sparc64'))
SUPERH_REGEX = RegexLazyIgnore(BOUNDED_REGEX.format('sh4'))
WINDOWS_REGEX = RegexLazyIgnore(
    BOUNDED_REGEX.format('64-?bit|WOW64|(?:Intel)?x64|WINDOWS_64|win64|.*amd64|.*x86_?64')
)
x86_REGEX = RegexLazyIgnore(BOUNDED_REGEX.format('.*32bit|.*win32|(?:i[0-9]|x)86|i86pc'))
CORASICK_COVERED_PLATFORMS = RegexLazyIgnore(
    r'RazoDroiD|MildWild|CyanogenMod|gNewSense|Coolita OS QJY|ClearPHONE|RokuBrowser|centos|playstation'
)


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
        if self.client_hints and self.client_hints.mobile:
            return self.client_hints.is_desktop()
        return self.family() in self.DESKTOP_OS

    def short_name(self) -> str:
        return self.ua_data.get('short_name', '')

    def family(self) -> str:
        return self.ua_data.get('family', '')

    def is_known(self) -> bool:
        if self.short_name() == self.UNKNOWN:
            return False
        return super().is_known()

    def check_all_regexes(self) -> bool | list:
        if check_all := super().check_all_regexes():
            return check_all
        return self.is_ios_fragment()

    def platform(self) -> str:
        if ch := self.client_hints:
            ch_architecture = self.client_hints.architecture.lower()
            if 'arm' in ch_architecture:
                return 'ARM'
            if 'loongarch64' in ch_architecture:
                return 'LoongArch64'
            if 'mips' in ch_architecture:
                return 'MIPS'
            if 'sh4' in ch_architecture:
                return 'SuperH'
            if 'sparc64' in ch_architecture:
                return 'SPARC64'
            if 'x64' in ch_architecture or (ch.bitness == '64' and 'x86' in ch_architecture):
                return 'x64'
            if ch_architecture == 'x86':
                return 'x86'
            return ch_architecture

        user_agent = self.user_agent
        if ARM_REGEX.search(user_agent):
            return 'ARM'
        if LOONGARCH_REGEX.search(user_agent):
            return 'LoongArch64'
        if MIPS_REGEX.search(user_agent):
            return 'MIPS'
        if SUPERH_REGEX.search(user_agent):
            return 'SuperH'
        if SPARK_REGEX.search(user_agent):
            return 'SPARC64'
        if WINDOWS_REGEX.search(user_agent):
            return 'x64'
        if x86_REGEX.search(user_agent):
            return 'x86'
        return ''

    def _parse(self) -> None:
        super()._parse()
        if not self.ua_data:
            OSFragment(
                self.user_agent,
                self.ua_spaceless,
                self.client_hints,
            ).parse()

    def set_details(self) -> None:
        super().set_details()
        os_from_ua = self.parse_os_from_useragent()
        os_from_hints = self.parse_os_from_client_hints()

        name_from_ua = os_from_ua.get('name')
        short_name_from_ua = os_from_ua.get('short_name')
        family_from_ua = os_from_ua.get('family')
        version_from_ua = os_from_ua.get('version')

        if os_from_hints:
            name = os_from_hints.get('name')
            short = os_from_hints.get('short_name') or short_name_from_ua
            family = os_from_hints.get('family') or family_from_ua
            version = os_from_hints.get('version') or ''
            ch_model = self.client_hints.model if self.client_hints else ''

            # Use version from user agent if non was provided in client hints,
            # but os family from useragent matches
            if not version and family_from_ua == family:
                version = version_from_ua

            if name == 'Windows' and version and version[0] == '0':
                version = '' if version_from_ua == '10' else version_from_ua

            # If the OS name detected from client hints matches the OS family from user agent
            # but the os name is another, use the one from user agent, as it might be more detailed
            if name == family_from_ua and name != name_from_ua:
                name = name_from_ua

                if name == 'LeafOS' or name == 'HarmonyOS':
                    version = ''
                elif name == 'PICO OS':
                    version = version_from_ua
                elif name == 'Fire OS' and os_from_hints:
                    major_version = version.split('.')[0] or '0'
                    version = FIREOS_VERSION_MAPPING.get(version) or FIREOS_VERSION_MAPPING.get(
                        major_version, version_from_ua
                    )

            # Chrome OS is in some cases reported as Linux in client hints,
            # we fix this only if the version matches
            if name == 'GNU/Linux' and name_from_ua == 'Chrome OS' and version == version_from_ua:
                name = name_from_ua
                short = short_name_from_ua

            # Chrome OS is in some cases reported as Android in client hints
            if name == 'Android' and (name_from_ua == 'Chrome OS' or ch_model in CHROME_OS_MODELS):
                name = 'Chrome OS'
                version = ''
                short = 'COS'

            # Meta Horizon is reported as Linux in client hints
            if name == 'GNU/Linux' and name_from_ua == 'Meta Horizon':
                name = name_from_ua
                short = short_name_from_ua
        elif name_from_ua:
            name = name_from_ua
            family = family_from_ua
            version = version_from_ua
            short = short_name_from_ua
        else:
            return

        if ch := self.client_hints:
            if ch.app in ANDROID_APPS and name != 'Android':
                name = 'Android'
                family = 'Android'
                short = 'ADR'
                version = ''
            elif ch.app == 'org.lineageos.jelly' and name != 'Lineage OS':
                major_version = version.split('.')[0] or '0'
                name = 'Lineage OS'
                family = 'Android'
                short = 'LEN'
                version = (
                    LINEAGEOS_VERSION_MAPPING.get(version)
                    or LINEAGEOS_VERSION_MAPPING.get(major_version)
                    or ''
                )
            elif ch.app == 'org.mozilla.tv.firefox' and name != 'Fire OS':
                major_version = version.split('.')[0] or '0'
                name = 'Fire OS'
                family = 'Android'
                short = 'FIR'
                version = (
                    FIREOS_VERSION_MAPPING.get(version)
                    or FIREOS_VERSION_MAPPING.get(major_version)
                    or ''
                )

        self.ua_data |= {
            'name': name,
            'short_name': short,
            'version': version,
            'platform': self.platform(),
            'family': family,
        }

    def parse_os_from_client_hints(self) -> dict:
        """
        Returns the OS that can be safely detected from client hints
        """
        if not (ch := self.client_hints):
            return {}

        os_data = {}
        if ch.architecture:
            os_data['platform'] = self.platform()
        if ch.platform_version:
            os_data['version'] = ch.platform_version
        if ch.platform:
            name_from_ua = os_data.get('name')
            if not name_from_ua or name_from_ua == 'Linux':
                os_data |= {
                    'name': ch.platform,
                    'family': self.FAMILY_FROM_OS.get(ch.platform, ch.platform),
                    'short_name': self.OS_TO_ABBREV.get(ch.platform.lower(), ''),
                }

        if not os_data and ch.client_hints_map:
            for os, version in ch.client_hints_map.items():
                osl = os.lower()
                if abbreviation := self.OS_TO_ABBREV.get(osl):
                    os_data = {
                        'name': os,
                        'short_name': abbreviation,
                        'version': version,
                        'family': self.FAMILY_FROM_OS.get(abbreviation, ''),
                    }
                    break

        if os_data:
            os_name = self.ua_data.get('name')
            version = os_data.get('version', '')

            if os_name == 'Windows':
                os_version = version.split('.')
                major_version = os_version[0] or '0'
                minor_version = '0' if len(os_version) == 1 else os_version[1]

                if major_version == '0':
                    minor_version_map = {'1': '7', '2': '8', '3': '8.1'}
                    version = minor_version_map.get(minor_version, version)
                elif '0' < major_version < '11':
                    version = '10'
                elif major_version > '10':
                    version = '11'

            # On Windows, version 0.0.0 can be either 7, 8 or 8.1, so we return 0.0.0
            elif os_name != 'Windows' and version == '0':
                version = ''

            os_data['version'] = version
            self.ua_data |= os_data

        return os_data

    def parse_os_from_useragent(self) -> dict:
        """
        Returns the OS that can be detected from useragent
        """
        if self.ua_data:
            name = normalized_name(
                self.ua_data['name'].lower(),
                self.OS_TO_ABBREV,
                self.OPERATING_SYSTEMS,
            )
            abbreviation = self.OS_TO_ABBREV.get(name.lower(), self.UNKNOWN)
            return {
                'name': name,
                'short_name': abbreviation,
                'family': self.FAMILY_FROM_OS.get(abbreviation),
                'version': self.set_version(self.ua_data.get('version', '')),
            }
        return {}

    def set_version(self, version: str) -> str:
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
