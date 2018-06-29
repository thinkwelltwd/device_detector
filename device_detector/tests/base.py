"""
device_detector Test Cases. Run entire suite by:

python3 -m unittest

Run individual test class by:

python3 -m unittest device_detector.tests.parser.test_bot
"""
import unittest
import yaml
try:
    from yaml import CSafeLoader as SafeLoader
except ImportError:
    from yaml import SafeLoader

from ..settings import ROOT



class Base(unittest.TestCase):

    fixture_files = []
    Parser = None

    def assertEqual(self, first, second, msg=None):
        if first == 'None':
            first = None
        if second == 'None':
            second = None
        # Count all falsy types as equal
        if not first and not second:
            return

        if not msg and hasattr(self, 'user_agent'):
            msg = '\n\nFailed to parse "{}"\n' \
                  'Parsed value {} != expected value {}'.format(
                getattr(self, 'user_agent'), first, second,
            )

        super().assertEqual(first, second, msg)

    def load_fixtures(self):
        fixtures = []
        for ffile in self.fixture_files:
            with open('{}/{}'.format(ROOT, ffile), 'r') as r:
                fixtures.extend(yaml.load(r, SafeLoader))
        return fixtures


class DetectorBaseTest(Base):
    Parser = None

    def get_value(self, fixture, key1, key2):
        """
        Helper function to get values from keys, where keys may not exist
        """
        if not fixture:
            return ''

        if key1 not in fixture:
            return ''

        if not fixture[key1] or key2 not in fixture[key1]:
            return ''

        return str(fixture[key1][key2])

    def test_parsing(self):

        if not self.Parser:
            return

        for fixture in self.load_fixtures():
            self.user_agent = fixture.pop('user_agent')
            device = self.Parser(self.user_agent)
            device.parse()

            # OS properties
            self.assertEqual(device.os_name(), self.get_value(fixture, 'os', 'name'))
            self.assertEqual(device.os_short_name(), self.get_value(fixture, 'os', 'short_name'))
            self.assertEqual(device.os_version(), self.get_value(fixture, 'os', 'version'))

            # Client properties
            self.assertEqual(device.client_name(), self.get_value(fixture, 'client', 'name'))
            self.assertEqual(device.client_type(), self.get_value(fixture, 'client', 'type'))
            self.assertEqual(str(device.client_version()), self.get_value(fixture, 'client', 'version'))

            # Device properties
            self.assertEqual(device.device_type(), self.get_value(fixture, 'device', 'type'))
            self.assertEqual(device.device_model(), self.get_value(fixture, 'device', 'model'))
            self.assertEqual(device.device_brand(), self.get_value(fixture, 'device', 'brand'))


class ParserBaseTest(Base):

    fixture_files = []
    fixture_key = 'client'   # key of fixture dict containing the values to compare
    fields = []
    Parser = None

    def load_fixtures(self):
        fixtures = []
        for ffile in self.fixture_files:
            with open('{}/{}'.format(ROOT, ffile), 'r') as r:
                fixtures.extend(yaml.load(r, SafeLoader))
        return fixtures

    def test_parsing(self):
        if not self.Parser or not self.fields:
            return

        fixtures = self.load_fixtures()

        for fixture in fixtures:
            self.user_agent = fixture.pop('user_agent')
            expect = fixture[self.fixture_key]
            parsed = self.Parser(self.user_agent).parse()
            data = parsed.ua_data

            for field in self.fields:
                self.assertIn(
                    field, data,
                    msg='Error parsing {}. '
                        'Parsed data does not have "{}" key'.format(self.user_agent, field))
                self.assertEqual(
                    str(expect[field]), str(data[field]),
                    msg='Error parsing {}. \n'
                        'Field "{}" parsed value "{}" != expected value "{}"'.format(
                        self.user_agent, field, data[field], expect[field]
                    )
                )



if __name__ == '__main__':
    unittest.main()
