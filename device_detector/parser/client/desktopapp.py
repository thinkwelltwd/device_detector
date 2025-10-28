from . import BaseClientParser
from device_detector.enums import AppType


class DesktopApp(BaseClientParser):
    __slots__ = ()
    APP_TYPE = AppType.DesktopApp

    fixture_files = [
        'local/client/desktop_apps.yml',
    ]


class OsUtility(BaseClientParser):
    __slots__ = ()
    APP_TYPE = AppType.OsUtility

    fixture_files = [
        'local/client/osutility.yml',
    ]


class Antivirus(BaseClientParser):
    __slots__ = ()
    APP_TYPE = AppType.Antivirus

    fixture_files = [
        'local/client/antivirus.yml',
    ]


__all__ = (
    'DesktopApp',
    'Antivirus',
    'OsUtility',
)
