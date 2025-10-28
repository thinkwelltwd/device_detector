from .base import BaseDeviceParser
from device_detector.enums import DeviceType
from ...lazy_regex import RegexLazyIgnore
from ...settings import BOUNDED_REGEX, DDCache


class BaseTvParser(BaseDeviceParser):
    __slots__ = ()

    def set_device_type(self) -> None:
        """
        Set device type, at least,since we know this is a TV.
        """
        if not self.ua_data:
            self.ua_data = {
                'brand': '',
                'model': '',
                'type': self.dtype(),
            }


class HbbTv(BaseTvParser):
    __slots__ = ()
    DEVICE_TYPE = DeviceType.TV

    @property
    def regex_list(self) -> list:
        cache_key = 'tv_regexes'
        if regexes := DDCache.get(cache_key, []):
            return regexes

        regexes = self.load_from_yaml('regexes/upstream/device/televisions.yml')
        if not regexes:
            return []

        reg_list = []
        for brand, stats in regexes.items():
            brand_data = {
                'brand': brand,
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

        DDCache[cache_key] = reg_list

        return reg_list

    def _parse(self) -> None:
        if self.is_hbbtv():
            super()._parse()
            return self.set_device_type()


class ShellTv(BaseTvParser):
    __slots__ = ()
    fixture_files = [
        'upstream/device/shell_tv.yml',
    ]

    def _parse(self) -> None:
        if self.is_shell_tv():
            super()._parse()
            return self.set_device_type()


__all__ = (
    'HbbTv',
    'ShellTv',
)
