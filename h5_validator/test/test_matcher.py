import os
import random
import shutil
import unittest
import logging
import sys
import h5py as h5

from h5_validator.matcher import KeyMatcher

logger = logging.getLogger()
logger.level = logging.DEBUG
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)

tmp_folder = os.path.join(os.path.dirname(__file__), "tmp_matcher")


class MatcherTest(unittest.TestCase):
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

    def test_exact_match(self):
        m = KeyMatcher(
            {},
            name="test",
            name_type="exact",
            count={'minimum_count': 1, 'maximum_count': 100}
        )

        self.assertFalse(m.is_satisfied)

        g1 = self.test_file.create_group("pie").create_group("test")
        self.assertTrue(m.try_match(g1))

        g2 = self.test_file.create_group("pork").create_group("tast")
        self.assertFalse(m.try_match(g2))

        self.assertTrue(m.is_satisfied)

    def test_regex_match(self):
        m = KeyMatcher(
            {},
            name="t[ea]st",
            name_type="regex",
            count={'minimum_count': 1, 'maximum_count': 100}
        )

        self.assertFalse(m.is_satisfied)

        g1 = self.test_file.create_group("pie").create_group("test")
        self.assertTrue(m.try_match(g1))

        g2 = self.test_file.create_group("pork").create_group("tast")
        self.assertTrue(m.try_match(g2))

        g2 = self.test_file.create_group("thing").create_group("tust")
        self.assertFalse(m.try_match(g2))

        self.assertTrue(m.is_satisfied)

    def test_match_count(self):
        m = KeyMatcher(
            {},
            name="t.st",
            name_type="regex",
            count=2
        )

        self.assertFalse(m.is_satisfied)

        g1 = self.test_file.create_group("test")
        self.assertTrue(m.try_match(g1))

        g2 = self.test_file.create_group("tast")
        self.assertTrue(m.try_match(g2))

        g1 = self.test_file.create_group("tust")
        self.assertFalse(m.try_match(g1))

        self.assertTrue(m.is_satisfied)

    def test_match_count_minmax(self):
        m = KeyMatcher(
            {},
            name="test[0-9]+",
            name_type="regex",
            count={'minimum_count': 0, 'maximum_count': 2}
        )

        self.assertTrue(m.is_satisfied)

        g1 = self.test_file.create_group("test1")
        self.assertTrue(m.try_match(g1))

        g2 = self.test_file.create_group("test2")
        self.assertTrue(m.try_match(g2))

        g3 = self.test_file.create_group("test3")
        self.assertFalse(m.try_match(g3))

        self.assertTrue(m.is_satisfied)

    def test_match_dataset(self):
        m = KeyMatcher(
            {},
            name="test",
            type="dataset",
            name_type="exact",
            count={'minimum_count': 1, 'maximum_count': 100}
        )

        self.assertFalse(m.is_satisfied)

        self.assertTrue(
            m.try_match(
                self.test_file.create_group("pie").create_dataset("test",
                                                                  data=[0])))
        self.assertFalse(
            m.try_match(
                self.test_file.create_group("pork").create_group("test")))
        self.test_file.create_group("thing").attrs.create("test", 5)
        self.assertFalse(
            m.try_match(
                self.test_file["thing"].attrs["test"], name="test",
                type="attribute"))

        self.assertTrue(m.is_satisfied)

    def test_match_attribute(self):
        m = KeyMatcher(
            {},
            name="test",
            type="attribute",
            name_type="exact",
            count={'minimum_count': 1, 'maximum_count': 100}
        )

        self.assertFalse(m.is_satisfied)

        self.assertFalse(
            m.try_match(
                self.test_file.create_group("pie").create_dataset("test",
                                                                  data=[0])
            )
        )
        self.assertFalse(
            m.try_match(
                self.test_file.create_group("pork").create_group("test")))
        self.test_file.create_group("thing").attrs.create("test", 5)
        self.assertTrue(
            m.try_match(
                self.test_file["thing"].attrs["test"], name="test",
                type="attribute")
        )

        self.assertTrue(m.is_satisfied)

    def test_match_group(self):
        m = KeyMatcher(
            {},
            name="test",
            type="group",
            name_type="exact",
            count={'minimum_count': 1, 'maximum_count': 100}
        )

        self.assertFalse(m.is_satisfied)

        self.assertFalse(
            m.try_match(
                self.test_file.create_group("pie").create_dataset("test",
                                                                  data=[0])))
        self.assertTrue(
            m.try_match(
                self.test_file.create_group("pork").create_group("test")))
        self.test_file.create_group("thing").attrs.create("test", 5)
        self.assertFalse(
            m.try_match(
                self.test_file["thing"].attrs["test"], name="test",
                type="attribute")
        )

        self.assertTrue(m.is_satisfied)
