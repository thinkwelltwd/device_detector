from typing import Optional

try:
    import rapidjson as json
except ImportError:
    import json

from . import BaseClientParser
from ...utils import calculate_dtype


class DictUA(BaseClientParser):
    """
    Some UA strings can be loaded as dicts directly, or with a little parsing.

    {"ac":"CCDesktop_app","av":"4.8.1.435"}
    {"locale":"en_US","appVersion":"5.2.5","os":"iOS","deviceName":"iPhone","deviceType":"phone","iOSApiLevel":"12.1.4","gzip":true,"appId":"KHAiOS","buildNumber":"31667"}
    target=LetGo; appVersion=1.58.0; bundle=com.letgo.ios; build=524; os=iOS 9.2.1; device=Apple iPad4,2; httpLibrary=Alamofire/4.7.3
    """

    def load_via_json(self):
        try:
            # sanity check - really shouldn't need to cast to dict.
            # at least 1 UA doesn't crash json.loads but remains a string.
            return dict(json.loads(self.user_agent))
        except Exception:
            return {}

    def parse_key_value_pairs(self):
        # AppName=iOSProApp;AppId=3;Platform=iOS;Model=iPad Pro 9.7-inch (Wi-Fi Cellular);OSVersion=12.0;Carrier=iPad;AppVersion=3.27.0.4
        try:
            return dict(item.strip().split("=") for item in self.user_agent.split(";"))
        except Exception:
            return {}

    def ua_as_dict(self) -> Optional[dict]:

        valid_json = self.load_via_json()
        if valid_json:
            return valid_json

        return self.parse_key_value_pairs()

    def _parse(self) -> None:
        """
        Each subclass may have `appdetails/<name>.yml` file(s) defined
        containing manually specified details for the regex.

        These files before checking regexes, for best performance.
        """
        ua_as_dict = self.ua_as_dict()
        if not ua_as_dict:
            return

        # descending order of interest!
        for name_key in (
                'app',
                'AppName',
                'target',
                'bundle',
                'bundleId',
                'bundleid',
                'BundleID',
                'ac',
                'appId',
        ):
            name = ua_as_dict.get(name_key, '')
            if name:
                self.app_name = name
                self.ua_data['name'] = name
                break

        # don't try to extract a version if we couldn't find a name
        if not self.ua_data:
            return

        # descending order of interest!
        for version_key in (
                'AppVersion',
                'appVersion',
                'version',
                'Version',
                'ver',
                'Ver',
                'av',
        ):
            version = ua_as_dict.get(version_key, '')
            if version:
                self.app_version = version_key
                self.ua_data['version'] = version
                break

    def dtype(self) -> str:
        return self.calculated_dtype or calculate_dtype(app_name=self.app_name)


__all__ = [
    'DictUA',
]
