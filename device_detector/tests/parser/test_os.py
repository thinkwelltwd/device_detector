from ..base import ParserBaseTest
from ...parser import OS


class TestOS(ParserBaseTest):

    fixture_files = [
        'tests/parser/fixtures/oss.yml',
    ]
    fields = ('name', 'short_name', 'version')
    fixture_key = 'os'
    Parser = OS


__all__ = (
    'TestOS',
)
