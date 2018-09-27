import logging
import os
import random
import shutil
import sys
import unittest
import h5py as h5
import numpy as np

from h5_validator.validator import Validator

logger = logging.getLogger()
logger.level = logging.DEBUG
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)

tmp_folder = os.path.join(os.path.dirname(__file__), "tmp_validator")


class ValidatorTest(unittest.TestCase):
    def setUp(self):
        fname = "".join((str(random.randint(0, 9)) for _ in range(8))) + ".h5"
        self.test_file = h5.File(os.path.join(tmp_folder, fname), "w")

    def tearDown(self):
        self.test_file.close()

    @classmethod
    def setUpClass(cls):
        if not os.path.exists(tmp_folder):
            os.makedirs(tmp_folder)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(tmp_folder):
            shutil.rmtree(tmp_folder)

    def test_dataset_match(self):
        test_dataset = self.test_file.create_dataset(
            "test",
            shape=(4, 3),
            dtype=np.dtype([('a', 'i4')]))

        self.assertTrue(Validator().validate_dataset(
            'i4',
            test_dataset
        ))

        self.assertFalse(Validator().validate_dataset(
            'i8',
            test_dataset
        ))

        self.assertTrue(Validator().validate_dataset(
            {'datatype': {'a': 'i4'}},
            test_dataset
        ))

        self.assertFalse(Validator().validate_dataset(
            {'datatype': {'b': 'i4'}},
            test_dataset
        ))

        self.assertFalse(Validator().validate_dataset(
            {'datatype': {'a': 'i8'}},
            test_dataset
        ))

        self.assertTrue(Validator().validate_dataset(
            {'datatype': {'a': 'i4'}, 'size': [4, 3]},
            test_dataset
        ))

        self.assertFalse(Validator().validate_dataset(
            {'datatype': {'a': 'i4'}, 'size': [3, 3]},
            test_dataset
        ))

        self.assertTrue(Validator().validate_dataset(
            {'datatype': {'a': 'i4'}, 'dimensions': 2},
            test_dataset
        ))

        self.assertFalse(Validator().validate_dataset(
            {'datatype': {'a': 'i4'}, 'dimensions': 1},
            test_dataset
        ))

    def test_attribute_match(self):
        self.test_file.attrs.create("test_int", 5)
        self.test_file.attrs.create("test_flt", 5.5)

        self.assertTrue(Validator().validate_attribute(
            'i4',
            self.test_file,
            "test_int"
        ))

        self.assertTrue(Validator().validate_attribute(
            'f4',
            self.test_file,
            "test_int"
        ))

        self.assertFalse(Validator().validate_attribute(
            'i4',
            self.test_file,
            "test_flt"
        ))

        self.assertTrue(Validator().validate_attribute(
            'f4',
            self.test_file,
            "test_flt"
        ))
