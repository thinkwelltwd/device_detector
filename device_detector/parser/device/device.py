from .base import BaseDeviceParser
from ...lazy_regex import RegexLazyIgnore
from .vendor_fragment import VendorFragment
from ...settings import BOUNDED_REGEX, DDCache
from ..settings import normalized_name

android_fragment = RegexLazyIgnore(BOUNDED_REGEX.format('Android'))
desktop_fragment = RegexLazyIgnore(BOUNDED_REGEX.format('Desktop (x(?:32|64)|WOW64);'))
tablet_fragment = RegexLazyIgnore(BOUNDED_REGEX.format(r'Android( [\.0-9]+)?; Tablet;'))
mobile_fragment = RegexLazyIgnore(BOUNDED_REGEX.format(r'Android( [\.0-9]+)?; Mobile;'))
opera_tablet = RegexLazyIgnore(BOUNDED_REGEX.format('Opera Tablet'))
tv_fragment = RegexLazyIgnore(BOUNDED_REGEX.format('Opera TV Store|SmartTV|Tizen.+ TV .+$|WebTV'))
hbbtv_fragment = RegexLazyIgnore(BOUNDED_REGEX.format(r'HbbTV/([1-9]{1}(?:\.[0-9]{1}){1,2})'))
shell_tv_fragment = RegexLazyIgnore(BOUNDED_REGEX.format(r'[a-z]+[ _]Shell[ _]\w{6}'))
facebook_notebook_fragment = RegexLazyIgnore(BOUNDED_REGEX.format('FBMD/'))


class Device(BaseDeviceParser):

    # The order of files needs to be the same as the order of device
    # parser classes used in the matomo project, except for TVs
    # which are parsed separately
    fixture_files = [
        'upstream/device/consoles.yml',
        'upstream/device/car_browsers.yml',
        'upstream/device/cameras.yml',
        'upstream/device/portable_media_player.yml',
        'upstream/device/mobiles.yml',
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._is_running_android = None
        self._has_android_mobile_fragment = None
        self._has_android_tablet_fragment = None
        self._has_desktop_fragment = None

    # -----------------------------------------------------------------------------
    # UA parsing methods
    # -----------------------------------------------------------------------------
    def extract_model(self) -> None:
        """
        Brand has list of model regexes to parse
        """
        for model in self.ua_data.pop('models', []):
            matched_regex = self._check_regex(model['regex'])
            if not matched_regex:
                continue

            self.matched_regex = matched_regex
            self.ua_data.update(model)
            self.ua_data.pop('regex', None)

            # i.e. Sony Ericsson should override Sony
            if 'brand' in model:
                self.ua_data['name'] = self.ua_data.pop('brand')

            # Must return after first match! Later patterns could match
            # again and clobber the earlier, correct, values.
            return

    def _parse(self) -> None:
        """
        Loop through all brands of all device types trying to find
        a model. Returns the first device with model info.
        """
        super()._parse()

        if self.ua_data:
            self.extract_model()
            return

        # If no brand info was found, check known fragments
        self.ua_data = VendorFragment(
            self.user_agent,
            self.ua_hash,
            self.ua_spaceless,
            self.VERSION_TRUNCATION,
        ).parse().ua_data or {}

    def get_model(self):
        model = self.ua_data.get('model', None)
        if model == 'Build':
            return None
        return model.strip() if model else model

    def set_details(self) -> None:
        super().set_details()
        dtype = self.dtype()

        if self.ua_data or dtype:
            if dtype != 'desktop' and self.has_desktop_fragment():
                dtype = 'desktop'

            name = self.ua_data.get('name', self.UNKNOWN_NAME)
            self.ua_data.update({
                'type': dtype,
                'brand': normalized_name(name, self.BRAND_TO_ABBREV, self.DEVICE_BRANDS),
                'device': self.ua_data.get('device', None),
                'model': self.get_model(),
            })

    # -----------------------------------------------------------------------------
    # Data post-processing / analysis
    # -----------------------------------------------------------------------------
    def is_tv(self) -> bool:
        """
        All devices running Opera TV Store, Tizen TV or SmartTV
        are assumed to be a tv.
        """
        return tv_fragment.search(self.user_agent) is not None

    def is_hbbtv(self) -> bool:
        """
        HbbTV UA strings are only parsed by the televisions.yml file
        """
        return hbbtv_fragment.search(self.user_agent) is not None

    def is_shell_tv(self) -> bool:
        """
        Shell UA strings are only parsed by the shell_tv.yml file
        """
        return shell_tv_fragment.search(self.user_agent) is not None

    def has_android_tablet_fragment(self) -> bool:
        """
        Returns if the parsed UA contains the 'Android; Tablet;' fragment
        """
        if not self.is_running_android():
            return False

        if self._has_android_tablet_fragment is None:
            self._has_android_tablet_fragment = tablet_fragment.search(self.user_agent) is not None
        return self._has_android_tablet_fragment

    def has_android_mobile_fragment(self) -> bool:
        """
        Returns if the parsed UA contains the 'Android; Mobile;' fragment
        """
        if not self.is_running_android():
            return False

        if self._has_android_mobile_fragment is None:
            self._has_android_mobile_fragment = mobile_fragment.search(self.user_agent) is not None
        return self._has_android_mobile_fragment

    def has_desktop_fragment(self) -> bool:
        if self._has_desktop_fragment is None:
            self._has_desktop_fragment = desktop_fragment.search(self.user_agent) is not None
        return self._has_desktop_fragment

    def is_opera_tablet(self) -> bool:
        return opera_tablet.search(self.user_agent) is not None

    def is_running_android(self) -> bool:
        if self._is_running_android is None:
            self._is_running_android = android_fragment.search(self.user_agent) is not None
        return self._is_running_android

    def check_android_device(self) -> str:
        """
        Chrome on Android passes the device type based on the keyword 'Mobile'
        If it is present the device should be a smartphone, otherwise it's a tablet
        See https://developer.chrome.com/multidevice/user-agent#chrome_for_android_user_agent
        """
        if self.has_android_mobile_fragment():
            return 'smartphone'

        if self.has_android_tablet_fragment():
            return 'tablet'

        return ''

    def dtype(self) -> str:
        """Calculcate Device Type, based on various parameters"""
        if self.is_hbbtv():
            self.ua_data['device'] = 'tv'

        ua_type = self.ua_data.get('device', '')
        if ua_type:
            if ua_type != 'tv' and self.is_tv():
                return 'tv'

            # All detected feature phones running android are more likely a smartphone
            if ua_type == 'feature phone' and self.is_running_android():
                return 'smartphone'

            return ua_type

        android_device = self.check_android_device()
        if android_device:
            return android_device

        if self.is_opera_tablet():
            return 'tablet'

        return ''

    def model(self) -> str:
        return self.ua_data.get('model', '')

    def __str__(self):
        return '%s %s' % (self.model(), self.dtype())


class HbbTv(Device):

    @property
    def regex_list(self) -> list:

        regexes = DDCache.get('tvregexes', [])
        if regexes:
            return regexes

        regexes = self.load_from_yaml('regexes/upstream/device/televisions.yml')
        if not regexes:
            return []

        reg_list = []
        for brand, stats in regexes.items():
            brand_data = {
                'name': brand,
                'regex': RegexLazyIgnore(BOUNDED_REGEX.format(stats['regex'])),
                'device': stats['device'],
            }
            if 'models' in stats:
                for model in stats['models']:
                    model['regex'] = RegexLazyIgnore(BOUNDED_REGEX.format(model['regex']))
                brand_data['models'] = stats['models']
            if 'model' in stats:
                brand_data['model'] = stats['model']
            reg_list.append(brand_data)

        DDCache['tvregexes'] = reg_list

        return reg_list

    def _parse(self) -> None:
        if self.is_hbbtv():
            return super()._parse()


class Notebook(Device):
    fixture_files = [
        'upstream/device/notebooks.yml',
    ]

    def _parse(self) -> None:
        """
        Loop through all brands of all device types trying to find
        a model. Returns the first device with model info.
        """
        if facebook_notebook_fragment.search(self.user_agent):
            return super()._parse()


class ShellTv(Device):
    fixture_files = [
        'upstream/device/shell_tv.yml',
    ]

    def _parse(self) -> None:
        if self.is_shell_tv():
            return super()._parse()


__all__ = (
    'Device',
    'HbbTv',
    'Notebook',
    'ShellTv',
)
