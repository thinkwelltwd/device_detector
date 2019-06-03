from . import BaseClientParser


class VPNProxy(BaseClientParser):

    appdetails_files = [
        'appdetails/vpnproxy.yml',
    ]

    fixture_files = [
        'local/client/vpnproxy.yml',
    ]

    def dtype(self):
        return self.calculated_dtype or 'vpnproxy'


__all__ = [
    'VPNProxy',
]
