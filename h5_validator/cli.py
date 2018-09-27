"""CLI interface for validator."""
from __future__ import \
    unicode_literals, \
    print_function, \
    absolute_import, \
    division

import argparse
import logging
import os
import sys
import h5py
import pkg_resources

from h5_validator.schema import Schema
from h5_validator.validator import Validator


def _find_schema(schema):
    if os.path.exists(schema):
        return schema
    if schema in pkg_resources.resource_listdir('h5_validator', 'schemas/'):
        return pkg_resources.resource_filename('h5_validator',
                                               'schemas/{}'.format(schema))
    raise OSError("Schema '{}' could not be found on path "
                  "or in default package resources"
                  "".format(schema))


def validate(f, schema, verbose=True, reporter=sys.stdout):
    """
    Validate a file against a schema.

    :param filename: Filename to open
    :param schema: URI to a schema to find and use
    :return: If the validation was successful
    """
    sch = Schema(_find_schema(schema))

    if not isinstance(f, h5py.File):
        f = h5py.File(f, "r")

    v = Validator()
    v.validate_file(sch, f)
    v.print_report(reporter, f, verbose)
    return v.is_valid


def main():
    """Invoke validation from command line."""
    parser = argparse.ArgumentParser(description='Validate HDF5 file')
    parser.add_argument('schema',
                        help='The schema URI to use for validation')
    parser.add_argument('filename',
                        help='The file to validate')
    parser.add_argument('-v', '--verbose', required=False, default=False,
                        action='store_true', help='Show verbose output')
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug logging')

    args = parser.parse_args()

    logging.basicConfig(stream=sys.stdout,
                        level=logging.DEBUG if args.debug else logging.INFO)

    validate(args.filename, args.schema, args.verbose)


if __name__ == "__main__":
    main()
