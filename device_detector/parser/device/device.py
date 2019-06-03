try:
    import regex as re
except (ImportError, ModuleNotFoundError):
    import re
from .base import BaseDeviceParser
from .vendor_fragment import VendorFragment
from ...settings import DDCache

tablet_fragment = re.compile(r'Android( [\.0-9]+)?; Tablet;', re.IGNORECASE)
mobile_fragment = re.compile(r'Android( [\.0-9]+)?; Mobile;', re.IGNORECASE)
opera_tablet = re.compile(r'Opera Tablet', re.IGNORECASE)
tv_fragment = re.compile(r'HbbTV', re.IGNORECASE)


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

    # -----------------------------------------------------------------------------
    # UA parsing methods
    # -----------------------------------------------------------------------------
    @property
    def tv_regex_list(self) -> list:

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
                'regex': re.compile(stats['regex'], re.IGNORECASE),
                'device': stats['device'],
            }
            if 'models' in stats:
                for model in stats['models']:
                    model['regex'] = re.compile(model['regex'], re.IGNORECASE)
                brand_data['models'] = stats['models']
            if 'model' in stats:
                brand_data['model'] = stats['model']
            reg_list.append(brand_data)

        DDCache['tvregexes'] = reg_list

        return reg_list

    def _get_model(self, brand) -> None:
        """
        Brand has list of model regexes to parse
        """
        for model in brand.get('models', []):
            matched_regex = self._check_regex(model['regex'])
            if not matched_regex:
                continue

            self.matched_regex = matched_regex
            self.ua_data.update(model)
            self.ua_data.pop('regex', None)
            self.ua_data.pop('models', None)

            # Must return after first match! Later patterns could match
            # again and clobber the earlier, correct, values.
            return

    def _parse(self) -> None:
        """
        Loop through all brands of all device types trying to find
        a model. Returns the first device with model info.
        """
        if self.is_hbbtv_ua():
            regex_list = self.tv_regex_list
        else:
            regex_list = self.regex_list

        for brand in regex_list:
            self.matched_regex = self._check_regex(brand['regex'])
            self.ua_data = brand.copy()
            if self.matched_regex:
                if 'models' in brand:
                    self._get_model(brand)
                return

        # If no brand info was found, check known fragments
        self.ua_data = VendorFragment(
            self.user_agent,
            self.ua_hash,
            self.ua_spaceless,
        ).parse().ua_data or {}

    def get_model(self):
        model = self.ua_data.get('model', None)
        if model == 'Build':
            return None
        return model

    def set_details(self) -> None:
        super().set_details()
        dtype = self.dtype()
        if self.ua_data or dtype:
            self.ua_data.update({
                'type': dtype,
                'brand': self.brand_short_name(),
                'device': self.ua_data.get('device', None),
                'model': self.get_model(),
            })

    # -----------------------------------------------------------------------------
    # Data post-processing / analysis
    # -----------------------------------------------------------------------------
    def is_hbbtv_ua(self) -> bool:
        """
        HbbTV UA strings are only parsed by the televisions.yml file
        """
        return tv_fragment.search(self.user_agent) is not None

    def has_android_tablet_fragment(self) -> bool:
        """
        Returns if the parsed UA contains the 'Android; Tablet;' fragment
        """
        return tablet_fragment.search(self.user_agent) is not None

    def has_android_mobile_fragment(self) -> bool:
        """
        Returns if the parsed UA contains the 'Android; Mobile;' fragment
        """
        return mobile_fragment.search(self.user_agent) is not None

    def is_opera_tablet(self) -> bool:
        return opera_tablet.search(self.user_agent) is not None

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
        if self.is_hbbtv_ua():
            self.ua_data['device'] = 'tv'

        ua_type = self.ua_data.get('device', '')
        if ua_type:
            return ua_type

        android_device = self.check_android_device()
        if android_device:
            return android_device

        if self.is_opera_tablet():
            return 'tablet'

        return ''

    def brand_short_name(self) -> str:
        brand = self.ua_data.get('brand', '')
        if len(brand) == 2:
            return brand
        if brand.lower() in self.BRAND_TO_ABBREV:
            return self.BRAND_TO_ABBREV[brand.lower()]
        name = self.ua_data.get('name', '')
        return self.BRAND_TO_ABBREV.get(name.lower(), name)

    def model(self) -> str:
        return self.ua_data.get('model', '')


__all__ = [
    'Device',
]
