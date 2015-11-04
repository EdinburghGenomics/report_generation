import os
from bcbio_report import Bcbio_report
from report_generation.readers.mapping_stats_parsers import parse_bamtools_stats, parse_callable_bed_file, \
    parse_highdepth_yaml_file, parse_validate_csv
from test import TestReport

__author__ = 'tcezard'


class Test_mapping_stats(TestReport):
    def setUp(self):
        self.bamtools_stat_file = os.path.join(self.test_data_path,'bamtools_stats.txt')
        self.highdepth_yaml_file = os.path.join(self.test_data_path,'10015TA0004-sort-highdepth-stats.yaml')
        self.callable_bed_file = os.path.join(self.test_data_path,'10015TA0004-sort-callable.bed')
        self.grading_csv_file = os.path.join(self.test_data_path,'grading-summary-10015TA0004-join.csv')
        self.bcbio_dir = os.path.join(self.test_data_path,'10015TA0004')

    def test_parse_bamtools_stats(self):
        self.assertEqual(parse_bamtools_stats(self.bamtools_stat_file), (988805087, 975587288, 171911966, 949154225))

    def test_parse_callable_bed_file(self):
        self.assertEqual(parse_callable_bed_file(self.callable_bed_file),
                         {'CALLABLE': 2814699727, 'NO_COVERAGE': 279176028, 'LOW_COVERAGE': 8275650, 'EXCESSIVE_COVERAGE': 5761})

    def test_parse_highdepth_yaml_file(self):
        self.assertEqual(parse_highdepth_yaml_file(self.highdepth_yaml_file),30.156)

    def test_parse_validate_csv(self):
        self.assertEqual(parse_validate_csv(self.grading_csv_file),(2864065, 215287, 50886, 40395))

    def test_bcbio_reportp(self):
        report = Bcbio_report([self.bcbio_dir])
        print(report)
        self.assertTrue(report)