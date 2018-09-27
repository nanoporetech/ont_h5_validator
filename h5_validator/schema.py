"""Schema functions to load and build hdf5 schemas."""

from __future__ import \
    unicode_literals, \
    print_function, \
    absolute_import, \
    division

import yaml

try:
    from urllib.request import urlopen
except ImportError:
    # python 2 compatibility
    from urllib2 import urlopen


class Schema():
    """An HDF5 schema object."""

    def __init__(self, obj):
        """
        Create a new schema.

        The schema object can be provided directly, or a filename or URI can be
        given.

        :param uri: The URI to create from.
        """
        if isinstance(obj, str):
            # The schema given is some kind of handle which we try to open
            self.data = self._get_schema_content(obj)
        else:
            self.data = obj

    def _get_schema_content(self, uri):
        try:
            with open(uri, "r") as fh:
                contents = fh.read()
        except IOError:
            with urlopen(uri) as response:
                contents = response.read()
        return yaml.load(contents)
