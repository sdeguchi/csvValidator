import unittest
import csv


class TestCSV(unittest.TestCase):
    def setUp(self):
        pass

    def test_allowed_file(self):
        self.assertTrue(csv.allowed_file("test.csv"))

    def test_unallowed_file1(self):
        self.assertFalse(csv.allowed_file("test.xls"))

    def test_unallowed_file2(self):
        self.assertFalse(csv.allowed_file("testxls"))

if __name__ == '__main__':
    unittest.main()