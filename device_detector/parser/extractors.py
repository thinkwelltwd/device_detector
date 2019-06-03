try:
    import regex as re
except (ImportError, ModuleNotFoundError):
    import re
from ..settings import DDCache
from ..yaml_loader import RegexLoader

APP_ID = re.compile(r'\b([a-z]{2,5}\.[\w\d\.\-]+)', re.IGNORECASE)


class DataExtractor:
    """
    Regex will define a string value or 1-based index
    position of the desired metadata

    - regex: '(?:Apple-)?(?:iPhone|iPad|iPod)(?:.*Mac OS X.*Version/(\d+\.\d+)|; Opera)?'
      name: 'iOS'
      version: '$1'
    """

    # metadata value to extract / return
    # subclasses must override
    key = ''

    def __init__(self, metadata, groups):
        """
        :param metadata: dict of regex and associated metadata
            {'regex': <regex1>, 'name': 'iOS', 'version': '$1'}
            {'regex': <regex2>, 'name': 'Windows', 'version': '10'}
        :param groups: Tuple of groups from regex
            ('Debian', None)
            ('iOS', '8_2')
        """
        self.metadata = metadata
        self.groups = groups

    def get_value_from_regex(self, value) -> str:
        """
        Model / Name values may be in format of
        $<int> or <NamePrefix> $<int>

        'Xino Z$1 X$2

        Replace %<int> section replaced with {} for format string

        'Xino Z$1 X$2 -> 'Xino Z{} X{}

        Return interpolated string with value from regex group
        """
        chars = []
        indices = []
        index_int_next = False

        for char in value:
            if char != '$':
                if index_int_next:
                    indices.append(int(char) - 1)
                    index_int_next = False
                else:
                    chars.append(char)
            else:
                chars.append('{}')
                index_int_next = True

        value = ''.join(chars)

        # collect regex group values, substituting empty string for None
        group_values = []
        for pos in indices:
            try:
                if not self.groups[pos]:
                    group_values.append('')
                else:
                    group_values.append(self.groups[pos])
            except IndexError:
                return ''

        return value.format(*group_values).strip()

    def extract(self) -> str:
        value = self.metadata.get(self.key, '')
        if value and '$' in value:
            return self.get_value_from_regex(value)
        return value

    def __str__(self):
        return '%s Extractor' % self.__class__.__name__

    def __repr__(self):
        return '%s(%s, %s)' % (self.__class__.__name__, self.metadata, self.groups)


class ApplicationIDExtractor(RegexLoader):
    """
    Extract App Store IDs such as:

    extract APP IDs such as
    com.cloudveil.CloudVeilMessenger
    com.houzz.app
    com.google.Maps
    """
    key = 'app_id'

    def __init__(self, user_agent):
        self.user_agent = user_agent
        self.details = {}
        self.app_id = ''
        self.name = ''

    def ignored_appids(self):
        """
        Load Ignored App IDs from yaml file
        """
        return self.load_app_id_sets(name='ignored')

    def secondary_appids(self):
        """
        Load Seconadary App IDs from yaml file
        """
        return self.load_app_id_sets(name='secondary')

    def normalized_app_ids(self):
        normalized = DDCache['appids_normalized']
        if normalized:
            return normalized

        DDCache['appids_normalized'] = self.load_from_yaml('appids/normalized.yml')
        return DDCache['appids_normalized']

    def extract(self) -> dict:
        """
        Parse for "<tld>.<string.<string>.<string>" value

        In the (unlikely) event that multiple valid IDs
        are found, just return the first one.
        """
        if self.details:
            return self.details

        app_ids = set(APP_ID.findall(self.user_agent))
        scrubbed_ids = sorted(list(app_ids.difference(self.secondary_appids())))

        if scrubbed_ids:
            app_id = scrubbed_ids[0]
            if app_id.lower() in self.ignored_appids():
                return {}
            details = self.normalized_app_ids().get(app_id.lower(), {'app_id': app_id})
            # allow for only pretty_name to be defined in the normalized data file
            if 'app_id' not in details:
                details['app_id'] = app_id

            self.details = details

        return self.details

    def pretty_name(self):
        details = self.extract()
        name = self.details.get('name', '')

        if name:
            return name

        if not details:
            return ''

        self.details['name'] = ' '.join(details.get('app_id', '').split('.')[1:]).title()

        return self.details['name']

    def __str__(self):
        return '%s("%s")' % (self.__class__.__name__, self.user_agent)

    def __repr__(self):
        return '%s("%s")' % (self.__class__.__name__, self.user_agent)


class NameExtractor(DataExtractor):
    key = 'name'


class ModelExtractor(DataExtractor):
    key = 'model'

    def extract(self) -> str:
        value = super().extract()
        if not value:
            return value

        # normalize D510_TD / ETON-T730D_TD
        if value.endswith('_TD'):
            value = value[:-3]
        return value.replace('_', ' ')


class VersionExtractor(DataExtractor):
    key = 'version'

    def extract(self) -> str:
        value = super().extract()
        if not value:
            return value

        value = value.replace('_', '.')
        if value.endswith('.'):
            return value[:-1]

        return value


__all__ = (
    'ApplicationIDExtractor',
    'DataExtractor',
    'ModelExtractor',
    'NameExtractor',
    'VersionExtractor',
)
