import os
from bcbio_report import Bcbio_report
from report_generation.readers.mapping_stats_parsers import parse_bamtools_stats, parse_callable_bed_file
from test import TestReport

__author__ = 'tcezard'

from unittest import TestCase


class Test_mapping_stats(TestReport):
    def setUp(self):
        self.bamtools_stat_file = os.path.join(self.test_data_path,'bamtools_stats.txt')
        self.callable_bed_file = os.path.join(self.test_data_path,'10015AT0004-sort-callable.bed')
        self.bcbio_dir = os.path.join(self.test_data_path,'bcbio')

    def test_parse_bamtools_stats(self):
        self.assertEqual(parse_bamtools_stats(self.bamtools_stat_file), (988805087, 975587288, 171911966, 949154225))

    def test_parse_callable_bed_file(self):
        self.assertEqual(parse_callable_bed_file(self.callable_bed_file),
                         {'CALLABLE': 2814699727, 'NO_COVERAGE': 279176028, 'LOW_COVERAGE': 8275650, 'EXCESSIVE_COVERAGE': 5761})
    def test_bcbio_reportp(self):
        report = Bcbio_report([self.bcbio_dir])
        print(report)
        self.assertTrue(report)