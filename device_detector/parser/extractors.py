

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
        value = self.metadata[self.key]
        if value and '$' in value:
            return self.get_value_from_regex(value)
        return value


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
    'DataExtractor',
    'ModelExtractor',
    'NameExtractor',
    'VersionExtractor',
)
