"""
test_real_data.py verifying real files.
"""

import unittest
import logging
import sys
import os.path
from h5_validator.cli import validate

logger = logging.getLogger()
logger.level = logging.ERROR
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)

test_data = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data")


class RealDataTest(unittest.TestCase):
    """
    Tests for real work files
    """

    def test_full_validate(self):
        """
        Test full hdf5 files validate correctly
        """
        with open(os.devnull, 'w') as devnull:
            self.assertTrue(validate(
                os.path.join(test_data, "test.fast5"),
                os.path.join(test_data, "schema.yml"),
                reporter=devnull
            ))
