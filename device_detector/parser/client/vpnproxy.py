from . import BaseClientParser


class VPNProxy(BaseClientParser):

    fixture_files = [
        'local/client/vpnproxy.yml',
    ]

    def dtype(self):
        return 'vpnproxy'



__all__ = (
    'VPNProxy',
)
