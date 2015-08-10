import os
from report_generation.readers.mapping_stats_parsers import parse_bamtools_stats
from test import TestReport

__author__ = 'tcezard'

from unittest import TestCase


class Test_mapping_stats(TestReport):
    def setUp(self):
        self.bamtools_stat_file = os.path.join(self.test_data_path,'bamtools_stats.txt')

    def test_parse_bamtools_stats(self):
        print(parse_bamtools_stats(self.bamtools_stat_file))
        self.assertEqual(parse_bamtools_stats(self.bamtools_stat_file), (988805087, 975587288, 171911966, 949154225))

