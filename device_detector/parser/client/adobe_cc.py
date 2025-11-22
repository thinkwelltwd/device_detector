from . import BaseClientParser
from device_detector.enums import AppType
from ...lazy_regex import RegexLazyIgnore

ADOBE_CC = RegexLazyIgnore(r'\b(?P<name>[\w ]+)/(?P<version>[\.\d]+) com\.adobe\.[\w+\.-]+/')


class AdobeCC(BaseClientParser):
    """
    Check Adobe Creative Cloud apps.
    """

    CHECK_APP_ID = False
    __slots__ = ()
    APP_TYPE = AppType.DesktopApp

    def _parse(self) -> None:
        if adobe_app := ADOBE_CC.search(self.user_agent):
            name, version = adobe_app.groups()
            if not name.lower().startswith('adobe'):
                name = f'Adobe {name}'
            self.app_name = name
            self.app_version = version
            self.ua_data = {
                'name': name,
                'version': version,
                'type': self.APP_TYPE,
            }


__all__ = [
    'AdobeCC',
]
