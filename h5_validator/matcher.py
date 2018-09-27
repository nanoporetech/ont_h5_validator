"""Matchers used in schema validation."""
from __future__ import \
    unicode_literals, \
    print_function, \
    absolute_import, \
    division
import re
import logging
import h5py
import numpy


class KeyMatcher():
    """Matches HDF5 objects with name and count data."""

    def __init__(self, source, **kwargs):
        """
        Create a new key matcher from schema data.

        :param source: The schema data input
        """
        self.source = source
        if source is None:
            raise Exception("Expected source to be specified for {}"
                            .format(kwargs))

        self.data = kwargs
        self.accepted_count = 0
        self.error_logger = logging.getLogger("h5_validate.matcher.failures")
        self.success_logger = logging.getLogger("h5_validate.matcher.matches")

    @property
    def count(self):
        """
        Find normalised count data.

        :return: Normalised count information for this matcher
        """
        expected_count = self.data.get("count", 1)
        if isinstance(expected_count, dict):
            return expected_count

        return {
            'minimum_count': expected_count,
            'maximum_count': expected_count
        }

    @property
    def can_accept_more(self):
        """
        Find if this matcher can accept more matches.

        :return: Find if try_match will ever return True again
        """
        if 'maximum_count' not in self.count:
            return True
        return self.accepted_count < self.count['maximum_count']

    @property
    def is_satisfied(self):
        """
        Find if this matcher is satisfied.

        :return: Find if this matcher is currently satisfied
        """
        cnt = self.count
        if 'minimum_count' in cnt:
            if self.accepted_count < cnt['minimum_count']:
                return False

        if 'maximum_count' in cnt:
            if self.accepted_count > cnt['maximum_count']:
                return False

        return True

    def try_match(self, obj, name=None, type=None):
        """
        Try to match this key against this matcher.

        :param obj: The object to try and match against
        :param name: A forcible name for the object, if name is not
                     accessible on [obj] (ie: an attribute)
        :param type: A forcible type for the attribute, if the type
                     is not accessible (ie: an attribute)
        :return: If the match was successful
        """
        full_name = name
        name = full_name
        if not full_name:
            full_name = obj.name
            name = full_name.rsplit("/", 1)[1]

        if not self.can_accept_more:
            self.error_logger.debug(
                "Not matching %s, matcher %s already fully matched",
                full_name, self)
            return False

        actual_type = type
        if not actual_type:
            if isinstance(obj, h5py.Group):
                actual_type = "group"
            elif isinstance(obj, h5py._hl.attrs.AttributeManager):
                actual_type = "attribute"
            elif isinstance(obj, h5py._hl.dataset.Dataset):
                actual_type = "dataset"
            else:
                raise Exception("Unknown data type {}".format(obj))

        expected_type = self.data.get("type", "group")
        if actual_type != expected_type:
            self.error_logger.debug(
                "Not matching %s, matcher %s incorrect type "
                "(expected %s, got %s)",
                full_name, self, expected_type, actual_type)
            return False

        # Find the leaf name of [obj]

        name_type = self.data.get("name_type", "exact")

        if name_type == "exact":
            accepted = name == self.data["name"]
        elif name_type == "regex":
            regex = re.compile(self.data["name"])
            accepted = regex.match(name) is not None
        else:
            raise Exception("Unknown name match type {}".format(name_type))

        if not accepted:
            self.error_logger.debug("Not matching %s, matcher %s"
                                    " failed to find name match",
                                    full_name, self)
            return False

        self.accepted_count += 1
        self.success_logger.debug("Matched %s to matcher %s",
                                  full_name, self)
        return True

    def __repr__(self):
        """Format this matcher as a string."""
        return "<'{}', type={} match_type={} count={}>" \
            .format(self.data["name"],
                    self.data.get("type", "group"),
                    self.data.get("name_type", "exact"),
                    self.count)


class FieldMatcher():
    """
    FieldMatcher tests if a field correctly meets a schema definition.

    This includes checking name and type.

    The FieldMatcher is satisfied if it has been visited by the correct
    attribute, or it is optional.
    """

    def __init__(self, **kwargs):
        """Create a new field matcher from schema data."""
        self._name = kwargs.get('name')
        self._is_optional = kwargs.get('optional', False)
        self._type = numpy.dtype(kwargs.get('type'))
        self._matched = False

        self.error_logger = logging.getLogger("h5_validate.matcher.failures")
        self.success_logger = logging.getLogger("h5_validate.matcher.matches")

    @staticmethod
    def expand_field_matchers(obj):
        """
        Turn an object describing a dataset into a list of matchers.

        Acceptable inputs are:
            expand_field_matchers("i4")
            expand_field_matchers({ 'a': "i4", 'b': "f4"})

        :param obj: A dict of dataset descriptions, or a single string
                    describing a single field.
        :return: List of FieldMatchers
        """
        if isinstance(obj, str):
            return [FieldMatcher(name=None, type=obj)]

        if not isinstance(obj, dict):
            raise Exception("Expected datatype description to be a dictionary")

        matchers = []
        for name in obj:
            data = obj[name]
            is_optional = False
            if isinstance(data, str):
                datatype = data
            else:
                datatype = data['datatype']
                is_optional = data.get('optional', False)

            matchers.append(FieldMatcher(
                name=name,
                type=datatype,
                optional=is_optional))

        return matchers

    @property
    def can_accept_more(self):
        """
        Find if this matcher can accept more matches.

        :return: Find if the matcher can accept more
                 matches (ie: try_match will ever return True again)
        """
        return not self._matched

    @property
    def is_satisfied(self):
        """
        Find if this matcher is satisfied.

        :return: Find if the matcher has already been satisfied
        """
        return self._matched or self._is_optional

    def try_match(self, field):
        """
        Attempt to match this matcher against [field].

        :param field: The attribute to try and match
        :return: If [obj] matches correctly
        """
        if self._name:
            if not field[0] == self._name:
                self.error_logger.debug("Not matching %s, matcher %s"
                                        " failed to find name match",
                                        field, self)
                return False

        type = field[1]
        if not isinstance(type, str):
            type = type[0]
        act_type = numpy.dtype(type)

        is_varlen_string_exc = act_type == "object" and self._type == "S"
        is_string_length_mismatch_exc = False
        if (self._type == "S"):
            type_as_str = str(act_type)
            if len(type_as_str) > 1:
                # String checking should just check string are strings, ignore
                # length.
                is_string_length_mismatch_exc = type_as_str[1] == "S"
        is_exception = is_varlen_string_exc or is_string_length_mismatch_exc

        if act_type != self._type and not is_exception:
            self.error_logger.debug("Not matching %s, matcher %s"
                                    " failed to find type",
                                    field, self)
            return False

        self._matched = True
        return True

    def __str__(self):
        """Format this matcher as a string."""
        return "<'{}' type={} optional={}>" \
            .format(self._name,
                    self._type,
                    self._is_optional)


class AttributeMatcher():
    """
    AttributeMatcher tests if an attribute correctly meets a schema definition.

    It is only satisfied if its been visited by the correctly typed attribute
    """

    def __init__(self, obj):
        """Create a new attribute matcher from schema data."""
        self._type = obj
        if not isinstance(obj, str):
            self._type = obj['datatype']

    def try_match(self, obj):
        """
        Attempt to match this matcher against [obj].

        :param obj: The attribute to try and match
        :return: If [obj] matches correctly
        """
        x = numpy.array([obj], dtype='S')
        try:
            x.astype(self._type)
            return True
        except ValueError:
            return False
