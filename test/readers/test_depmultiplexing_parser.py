import os
from demultiplexing_report import  Demultiplexing_report
from report_generation.readers.demultiplexing_parsers import parse_conversion_stats, parse_demultiplexing_stats
from test import TestReport

__author__ = 'tcezard'


class Test_demultiplexing(TestReport):
    def setUp(self):
        self.xml_file1 = os.path.join(self.test_data_path,'DemultiplexingStats.xml')
        self.xml_file2 = os.path.join(self.test_data_path,'ConversionStats.xml')

    def test_parse_demultiplexing_stats(self):
        self.assertTrue(parse_demultiplexing_stats(self.xml_file1))

    def test_parse_conversion_stats(self):
        all_barcodes_per_lanes, top_unknown_barcodes_per_lanes = parse_conversion_stats(self.xml_file2)
        self.assertTrue(all_barcodes_per_lanes)
        self.assertTrue(top_unknown_barcodes_per_lanes)

    def test_demultiplexing_report(self):
        report = Demultiplexing_report(self.xml_file2)
        print(report)
        self.assertTrue(report)

