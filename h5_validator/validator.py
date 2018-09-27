"""Validator functions to verifying HDF5 object trees."""

from __future__ import \
    unicode_literals, \
    print_function, \
    absolute_import, \
    division
from h5_validator.matcher import KeyMatcher, FieldMatcher, AttributeMatcher
import h5py


class SchemaError(Exception):
    """An error which occured during validation."""

    def __init__(self, **kwargs):
        """Create new error."""
        self._data = kwargs

    def __str__(self):
        """
        Print report for this error.

        Should provide useful data to consumers of validations reports
        """
        return "Error at {}: \n    {}\n".format(self._data["object"].name,
                                                self._data["error"])


class Validator():
    """Validator provides top level access to validate HDF5 object trees."""

    def __init__(self):
        """
        Create a new validator.

        Users should now call validate_* functions to check
        validity of hdf objects.
        """
        self.errors = []

    @property
    def is_valid(self):
        """
        Find if this validator is valid.

        :return: Is this validator error free?
        """
        return len(self.errors) == 0

    def print_report(self, outputter, f, verbose=False):
        """
        Print a full report on errors this validator has encountered.

        Should provide useful data to users about why
        the file failed to validate.
        """
        if not self.errors:
            outputter.write("HDF5 file validated successfully: {}"
                            .format(f.filename))
        else:
            outputter.write("Validation encountered {} errors in {}\n\n"
                            .format(len(self.errors), f.filename))
            if verbose:
                for err in self.errors:
                    outputter.write(str(err))

    def validate_file(self, schema, file):
        """
        Validate a full file against [schema].

        :param schema: The schema to validate against
        :param file: The HDF5 file to validate
        :return: If the validation was error free
        """
        return self.validate_group(schema.data["file"], file)

    def validate_group(self, level, object):
        """
        Validate a group against a schema.

        :param level: The group schema to validate against
        :param object: The HDF5 object to validate
        :return: If the validation was error free
        """
        # Find the matchers available at this level
        matchers = self._build_matchers(level)
        child_pairs = {}

        extra_mode = level.get('extra_members', 'fail')

        # Match the matchers against the first level children
        # (datasets and groups)
        for k in object:
            found = False
            for m in matchers:
                obj = object[k]
                if m.try_match(obj):
                    found = True
                    child_pairs[obj] = m

            if not found:
                if (extra_mode == 'fail'):
                    self.errors.append(SchemaError(
                        error="Failed to match {} to item in schema"
                              "".format(object[k].name),
                        object=object[k],
                        matchers=matchers))

        # Match against attributes
        attrs = dict(object.attrs)
        for k in attrs:
            found = False
            for m in matchers:
                if m.try_match(attrs[k], name=k, type="attribute"):
                    child_pairs[k] = m
                    found = True

            if not found:
                self.errors.append(SchemaError(
                    error="Failed to match attribute '{}' in '{}' to schema"
                          "".format(k, object.name),
                    object=object,
                    attribute=k,
                    matchers=matchers))

        # Verify all matchers are satisfied completely
        for m in matchers:
            if not m.is_satisfied:
                self.errors.append(SchemaError(
                    error="Matcher {} was not satisfied after matching {}"
                          "".format(m, object),
                    object=object,
                    matchers=matchers))

        # Verify any child pairs which we discovered
        for child in child_pairs:
            matcher = child_pairs[child]

            if isinstance(child, h5py.Group):
                self.validate_group(matcher.data, child)
            elif isinstance(child, h5py._hl.dataset.Dataset):
                self.validate_dataset(matcher.source, child)
            elif isinstance(child, str):
                self.validate_attribute(matcher.source, object, child)
            else:
                try:
                    # HDF strings in python2 can be unicode
                    if isinstance(child, unicode):
                        self.validate_attribute(matcher.source, object, child)
                    else:
                        raise Exception("Unknown data type {}".format(child))
                except NameError:
                    pass

        return self.is_valid

    def validate_dataset(self, dataset, object):
        """
        Validate a dataset against a schema.

        :param dataset: The dataset schema to validate against
        :param object: The HDF5 object to validate
        :return: If the validation was error free
        """
        dataset = self._expand_dataset(dataset)

        matchers = FieldMatcher.expand_field_matchers(dataset['datatype'])

        actual_dtype = object.dtype
        if actual_dtype.fields is not None:
            fields = [(name, dtype.str)
                      for name, (dtype, size) in actual_dtype.fields.items()]
        else:
            fields = [('', actual_dtype.str)]

        for field in fields:
            found = False
            for m in matchers:
                if m.can_accept_more and m.try_match(field):
                    found = True

            if not found:
                self.errors.append(SchemaError(
                    error="Failed to match field {} to schema".format(field),
                    matchers=matchers,
                    object=object,
                    dataset=dataset))

        for m in matchers:
            if not m.is_satisfied:
                self.errors.append(SchemaError(
                    error="Failed to satisfy matcher {} to dataset".format(m),
                    matchers=matchers,
                    object=object,
                    dataset=dataset))

        if 'dimensions' in dataset:
            shape = object.shape
            if len(shape) != dataset['dimensions']:
                self.errors.append(SchemaError(
                    error="Invalid dimensions",
                    expected=dataset['dimensions'],
                    actual=len(shape),
                    object=object))

        if 'size' in dataset:
            shape = object.shape
            size = dataset['size']
            if len(shape) == len(size):
                for i in range(0, len(size)):
                    if shape[i] != size[i]:
                        self.errors.append(SchemaError(
                            error="Invalid shape dimension {}".format(i),
                            expected=size[i],
                            actual=shape[i],
                            object=object))
            else:
                self.errors.append(SchemaError(
                    error="Invalid shape dimensions",
                    expected=size,
                    actual=shape,
                    object=object))

        return self.is_valid

    def validate_attribute(self, attribute, object, name):
        """
        Validate an attribute against a schema.

        :param attribute: The parent schema to validate against
        :param object: The HDF5 object to validate
        :param name: The name of the attribute (on [object]) to validate
        :return: If the validation was error free
        """
        m = AttributeMatcher(attribute)
        value = object.attrs[name]

        if not m.try_match(value):
            self.errors.append(SchemaError(
                error="Failed to match attribute",
                expected=m,
                actual=value,
                object=object))

        return self.is_valid

    def _build_matchers(self, level):
        types = {
            "groups": "group",
            "attributes": "attribute",
            "datasets": "dataset",
        }

        matchers = []
        for type in types:
            items = level.get(type, {})
            for k in items:
                data = {}
                if items[k] is None:
                    raise Exception("Found empty element at {}".format(k))
                if isinstance(items[k], dict):
                    data = dict(items[k])
                data["name"] = k
                data["type"] = types[type]
                matchers.append(KeyMatcher(items[k], **data))
        return matchers

    def _expand_dataset(self, dataset):
        object = dataset
        if isinstance(dataset, str):
            object = {
                'datatype': dataset
            }

        if 'datatype' not in object:
            raise Exception("Expected datatype field in schema {}"
                            .format(dataset))

        return object
