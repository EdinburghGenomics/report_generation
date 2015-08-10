__author__ = 'tcezard'
from unittest import TestCase
import os.path


class TestReport(TestCase):
    test_data_path = os.path.join(os.path.dirname(__file__), 'test_data')
