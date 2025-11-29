from .base import BaseDeviceParser
from device_detector.enums import DeviceType
from ..parser import ENDSWITH_DARWIN, IPHONE_ONLY_UA
from ...lazy_regex import RegexLazy, RegexLazyIgnore
from .vendor_fragment import VendorFragment
from ...settings import BOUNDED_REGEX
from ..settings import ALWAYS_DESKTOP_OS, DESKTOP_OS

CHROME_FRAGMENT = RegexLazy(BOUNDED_REGEX.format(r'Chrome/[.0-9]*'))
CHROME_MOBILE_FRAGMENT = RegexLazy(BOUNDED_REGEX.format(r'(?:Mobile|eliboM)'))
DESKTOP_FRAGMENT = RegexLazy(BOUNDED_REGEX.format(r'(?:Windows (?:NT|IoT)|X11; Linux x86_64)'))
EXCLUDED_DESKTOP_FRAGMENT = RegexLazy(
    BOUNDED_REGEX.format(
        'CE-HTML|'
        ' Mozilla/|Andr[o0]id|Tablet|Mobile|iPhone|Windows Phone|ricoh|OculusBrowser|'
        'PicoBrowser|Lenovo|compatible; MSIE|Trident/|Tesla/|XBOX|FBMD/|ARM; ?([^)]+)'
    )
)
ANDROID_MOBILE_FRAGMENT = RegexLazy(
    BOUNDED_REGEX.format(r'Android( [.0-9]+)?; Mobile;|.*\-mobile$')
)
ANDROID_VRF_FRAGMENT = RegexLazy(BOUNDED_REGEX.format(r'Android( [.0-9]+)?; Mobile VR;| VR '))
ANDROID_TABLET_FRAGMENT = RegexLazy(
    BOUNDED_REGEX.format(r'Android( [.0-9]+)?; Tablet;|Tablet(?! PC)|.*\-tablet$')
)
ANDROID_TV_FRAGMENT = RegexLazyIgnore(
    BOUNDED_REGEX.format(r'Andr0id|(?:Android(?: UHD)?|Google) TV|\(lite\) TV|BRAVIA|Firebolt| TV$')
)
TOUCH_FRAGMENT = RegexLazy(BOUNDED_REGEX.format('Touch'))
GENERAL_TABLET_FRAGMENT = RegexLazy(BOUNDED_REGEX.format('HTC|Kindle'))
TV_FRAGMENT = RegexLazyIgnore(BOUNDED_REGEX.format(r'TV Store|WhaleTV|Smart TVS'))
TV_MINI_FRAGMENT = RegexLazyIgnore(BOUNDED_REGEX.format(r'\(TV;'))
TIZEN_TV_FRAGMENT = RegexLazy(BOUNDED_REGEX.format(r'SmartTV|Tizen.+ TV .+$'))

# Some UA contain the fragment 'Pad/APad', so we assume those devices as tablets
PAD_TABLET_FRAGMENT = RegexLazy(BOUNDED_REGEX.format(r'Pad/APad'))

PUFFIN_DESKTOP_FRAGMENT = RegexLazy(BOUNDED_REGEX.format(r'Puffin/(?:\d+[.\d]+)[LMW]D'))
PUFFIN_PHONE_FRAGMENT = RegexLazy(BOUNDED_REGEX.format(r'Puffin/(?:\d+[.\d]+)[AIFLW]P'))
PUFFIN_TABLET_FRAGMENT = RegexLazy(BOUNDED_REGEX.format(r'Puffin/(?:\d+[.\d]+)[AILW]T'))

OPERA_TABLET_FRAGMENT = RegexLazy(BOUNDED_REGEX.format('Opera Tablet'))
OPERA_TV_FRAGMENT = RegexLazy(BOUNDED_REGEX.format('Opera TV Store| OMI/'))

ENDSWITH_FIREFOX = RegexLazyIgnore(r'(Firefox|Iceweasel|Phoenix)/(?:\d+[.\d]+)$')


class Device(BaseDeviceParser):
    """
    This class should be the final device-type class checked.

    It should not be subclassed!
    """

    __slots__ = ()

    DEVICE_TYPE = DeviceType.Smartphone

    fixture_files = [
        'upstream/device/mobiles.yml',
    ]

    def check_all_regexes(self) -> bool:
        # Match relatively generic UAs like:
        # UCWEB/2.0 (MIDP-2.0; U; zh-CN; IQ4406) U2/1.0.0 UCBrowser/3.4.3.532 U2/1.0.0 Mobile
        # UCWEB/2.0 (Linux; U; Opera Mini/7.1.32052/30.3697; en-US; LG-E405) U2/1.0.0 UCBrowser/8.8.1.359 Mobile
        if self.user_agent_lower.endswith(' mobile'):
            return True

        if super().check_all_regexes():
            return True

        if self.user_agent_lower.startswith('iphone'):
            return IPHONE_ONLY_UA.match(self.user_agent) is not None

        if ENDSWITH_FIREFOX.search(self.user_agent) is not None:
            return True

        if ENDSWITH_DARWIN.search(self.user_agent) is not None:
            return True

        return self.user_agent_lower == 'msdw'

    def _parse(self) -> None:
        """
        Loop through all brands of all device types trying to find
        a model. Returns the first device with model info.
        """
        ch_model = self.client_hints and self.client_hints.model
        user_agent = self.user_agent
        ac_matched = self.check_all_regexes()
        if not ac_matched:
            return

        # ------------------------------------------------
        # Complete copy of the superclass _parse method
        for ua_data in self.regex_list:
            if self.known:
                break
            if matched := ua_data['regex'].search(user_agent):
                self.matched_regex = matched
                self.ua_data |= {k: v for k, v in ua_data.items() if k != 'regex'}
                self.known = True
            elif ch_model:
                main_fixture_dtype = ua_data.get('device')
                if ua_models := ua_data.get('models', []):
                    for model_data in ua_models:
                        if self.known:
                            break
                        model_fixture_dtype = model_data.get('device', main_fixture_dtype)
                        if model_fixture_dtype != self.DEVICE_TYPE:
                            continue
                        matched = model_data['regex'].search(ch_model)
                        if matched:
                            self.matched_regex = matched
                            self.known = True
                            ua_data = {
                                k: v for k, v in ua_data.items() if k != 'regex' and k != 'models'
                            }
                            ua_data['model'] = model_data['model']
                            ua_data['device'] = model_fixture_dtype
                            self.ua_data = ua_data

                elif main_fixture_dtype == self.DEVICE_TYPE and (
                    matched := ua_data['regex'].search(ch_model)
                ):
                    self.matched_regex = matched
                    self.ua_data |= {k: v for k, v in ua_data.items() if k != 'regex'}
                    self.known = True
        # ------------------------------------------------

        if not self.ua_data:
            if ch := self.client_hints:
                self.ua_data |= {
                    'type': ch.device_type(),
                    'model': ch.model,
                    'brand': 'Apple' if ch.platform == 'Mac' else '',
                }

        if not self.ua_data.get('brand'):
            # If no brand info was found, check known fragments
            vendor_fragment = (
                VendorFragment(self.user_agent, self.ua_spaceless, self.client_hints)
                .parse()
                .ua_data
            )
            if vendor_fragment:
                self.ua_data |= vendor_fragment

        if device_type := self.dtype():
            self.ua_data['type'] = device_type

        # if ac_matched and not isinstance(ac_matched, bool) and not self.ua_data:
        #     print(f'{self.cache_name}: Unwanted AC Match is {ac_matched}')

    def is_tablet(self) -> bool:
        """
        Check for various tablet fragments.
        """
        return PAD_TABLET_FRAGMENT.search(self.user_agent) is not None

    def check_android_device(
        self,
        dtype: DeviceType | str,
        os_name: str,
        os_version: str,
    ) -> DeviceType | None:
        """
        Chrome on Android passes the device type based on the keyword 'Mobile'
        If it is present the device should be a smartphone, otherwise it's a tablet
        See https://developer.chrome.com/multidevice/user-agent#chrome_for_android_user_agent
        """
        if os_name not in ('Android', 'MocorDroid'):
            return None

        # All detected feature phones running Android are more likely a smartphone
        if dtype == DeviceType.FeaturePhone:
            return DeviceType.Smartphone

        if not self.matched_regex:
            # All devices containing VR fragment are assumed to be a wearable
            if ANDROID_VRF_FRAGMENT.search(self.user_agent) is not None:
                return DeviceType.Wearable

            # Some UA contain the fragment 'Android; Tablet;' or 'Opera Tablet',
            # so we assume those devices as tablets
            if (
                ANDROID_TABLET_FRAGMENT.search(self.user_agent) is not None
                or OPERA_TABLET_FRAGMENT.search(self.user_agent) is not None
            ):
                return DeviceType.Tablet

            if ANDROID_MOBILE_FRAGMENT.search(self.user_agent) is not None:
                return DeviceType.Smartphone

            # Chrome on Android passes the device type based on the keyword 'Mobile'
            # If it is present the device should be a smartphone, otherwise it's a tablet
            # See https://developer.chrome.com/multidevice/user-agent#chrome_for_android_user_agent
            # Note: We do not check for browser (family) here, as there might be mobile apps using
            #       Chrome, that won't have a detected browser, but can still be detected.
            #       So we check the useragent for Chrome instead.
            if CHROME_FRAGMENT.search(self.user_agent) is not None:
                if CHROME_MOBILE_FRAGMENT.search(self.user_agent) is not None:
                    return DeviceType.Smartphone
                return DeviceType.Tablet

            # Android up to 3.0 was designed for smartphones only. But as 3.0, which was tablet
            # only, was published too late, there were a bunch of tablets running with 2.x
            #
            # With 4.0 the two trees were merged and it is for smartphones and tablets
            # So were are expecting that all devices running Android < 2 are smartphones
            # Devices running Android 3.X are tablets. Device type of Android 2.X and 4.X+
            # are unknown
            if not os_version:
                return None

            try:
                if float(os_version) < 2.0:
                    return DeviceType.Smartphone
                if 3.0 <= float(os_version) < 4.0:
                    return DeviceType.Tablet
            except (ValueError, TypeError):
                pass

        return None

    def check_puffin_device(self) -> DeviceType | None:
        if self.matched_regex:
            return None

        # All devices running Puffin Secure Browser that contain
        # letter 'D' are assumed to be desktops
        if PUFFIN_DESKTOP_FRAGMENT.search(self.user_agent) is not None:
            return DeviceType.Desktop

        # All devices running Puffin Web Browser that contain
        # letter 'P' are assumed to be smartphones
        if PUFFIN_PHONE_FRAGMENT.search(self.user_agent) is not None:
            return DeviceType.Smartphone

        # All devices running Puffin Web Browser that contain
        # letter 'T' are assumed to be tablets
        if PUFFIN_TABLET_FRAGMENT.search(self.user_agent) is not None:
            return DeviceType.Tablet

        return None

    def is_television(self, os_name: str) -> bool:
        """
        Check all the ways a device might be a television.
        """
        # All devices running Coolita OS are assumed to be a tv
        if os_name == 'Coolita OS':
            return True

        # All devices running Opera TV Store are assumed to be a tv
        if OPERA_TV_FRAGMENT.search(self.user_agent) is not None:
            return True

        if ANDROID_TV_FRAGMENT.search(self.user_agent) is not None:
            return True

        # All devices running Tizen TV or SmartTV are assumed to be a tv
        if not self.matched_regex and TIZEN_TV_FRAGMENT.search(self.user_agent) is not None:
            return True

        # All devices containing TV fragment are assumed to be a tv
        if TV_MINI_FRAGMENT.search(self.user_agent) is not None:
            return True

        if TV_FRAGMENT.search(self.user_agent) is not None:
            return True

        return False

    def is_desktop(self, os_name: str) -> bool:
        if os_name in ALWAYS_DESKTOP_OS:
            return True

        if os_name not in DESKTOP_OS or GENERAL_TABLET_FRAGMENT.search(self.user_agent) is not None:
            return False

        # Returns if the parsed UA contains the 'Windows NT;' or 'X11; Linux x86_64' fragments
        fragment = (
            DESKTOP_FRAGMENT.search(self.user_agent) is not None
            and EXCLUDED_DESKTOP_FRAGMENT.search(self.user_agent) is None
        )
        return fragment or os_name == 'Mac' or ' Desktop' in self.user_agent

    def device_runs_feature_phone_os(self, os_name: str) -> bool:
        if not self.matched_regex and os_name == 'Java ME':
            return True

        # All devices running KaiOS are more likely feature phones
        return os_name == 'KaiOS'

    def is_windows_tablet(self, os_name: str, os_version: str) -> bool:
        """
        According to https://msdn.microsoft.com/en-us/library/ie/hh920767(v=vs.85).aspx
        Internet Explorer 10 introduces the "Touch" UA string token. If this token is present
        at the end of the UA string, the computer has touch capability, and is running Windows 8
        (or later). This UA string will be transmitted on a touch-enabled system running
        Windows 8 (RT)

        As most touch enabled devices are tablets and only a smaller part are desktops/notebooks
        we assume that all Windows 8 touch devices are tablets.
        """
        if self.matched_regex:
            return False
        if os_name == 'Windows RT' or (os_name == 'Windows' and os_version.startswith('8')):
            return TOUCH_FRAGMENT.search(self.user_agent) is not None
        return False

    def dtype(self) -> DeviceType | str:
        """Calculate Device Type, based on various parameters"""
        default_dtype = super().dtype()
        fixture_dtype = self.device_type_from_fixture()

        os_name = self.os_details.get('name') or ''
        os_family = self.os_details.get('family') or ''
        os_version = self.os_details.get('version') or ''

        if self.device_runs_feature_phone_os(os_name):
            return DeviceType.FeaturePhone

        if self.client_hints and self.client_hints.is_television():
            return DeviceType.TV

        if android_device := self.check_android_device(fixture_dtype, os_name, os_version):
            return android_device

        if self.is_windows_tablet(os_name, os_version):
            return DeviceType.Tablet

        if device_from_puffin := self.check_puffin_device():
            return device_from_puffin

        if default_dtype != DeviceType.TV and self.is_television(os_name):
            return DeviceType.TV

        if default_dtype != DeviceType.Tablet and self.is_tablet():
            return DeviceType.Tablet

        if default_dtype != DeviceType.Desktop and self.is_desktop(os_name):
            return DeviceType.Desktop

        # Set device type to desktop for all devices running a
        # desktop OS that were not detected as another device type
        if not self.matched_regex and os_family in DESKTOP_OS:
            return DeviceType.Desktop

        if not self.user_agent:
            return DeviceType.Unknown

        return fixture_dtype or default_dtype

    def model(self) -> str:
        return self.ua_data.get('model', '')

    def __str__(self) -> str:
        return f'{self.model()} {self.dtype()}'


__all__ = [
    'Device',
]
