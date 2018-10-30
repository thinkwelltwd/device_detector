try:
    import regex as re
except ImportError:
    import re

APP_ID = re.compile(r'(com\.(?:[\w\d\-_]+\.)+(?:[\w\d\-_]+))', re.IGNORECASE)

# If UA string contains App ID IGNORE_APPIDS, consider it not to have an App ID at all
IGNORE_APPIDS = {
    'com.yourcompany.testwithcustomtabs',
    'com.yourcompany.speedboxlite',
}

# If UA string contains multiple App IDs, prefer any not in SECONDARY_APPIDS
SECONDARY_APPIDS = {
    'com.usebutton.sdk',
}
NORMALIZE_ID = {
    'com.apple.configurator.xpc.deviceservice': 'com.apple.configurator',
    'com.apple.configurator.xpc.internetservice': 'com.apple.configurator',
}


class DataExtractor(object):
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
            if not self.groups[pos]:
                group_values.append('')
            else:
                group_values.append(self.groups[pos])

        return value.format(*group_values).strip()

    def extract(self) -> str:
        value = self.metadata.get(self.key, '')
        if value and '$' in value:
            return self.get_value_from_regex(value)
        return value


class ApplicationIDExtractor:
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
        self.app_id = ''

    def extract(self):
        """
        arse for "com.<string.<string>.<string>" value

        In the (unlikely) event that multiple valid IDs
        are found, just return the first one.
        """
        if self.app_id:
            return self.app_id

        app_ids = set(APP_ID.findall(self.user_agent))
        scrubbed_ids = sorted(list(app_ids.difference(SECONDARY_APPIDS)))

        if scrubbed_ids:
            app_id = scrubbed_ids[0]
            if app_id.lower() in IGNORE_APPIDS:
                return ''
            self.app_id = NORMALIZE_ID.get(app_id.lower(), app_id)

        return self.app_id

    def pretty_name(self):
        app_id = self.extract()
        return ' '.join(app_id.split('.')[1:]).title()


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
