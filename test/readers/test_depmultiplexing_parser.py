from demultiplexing_report import demultiplexing_report_wiki
from report_generation.readers.demultiplexing_parsers import parse_conversion_stats, parse_demultiplexing_stats

__author__ = 'tcezard'

from unittest import TestCase


class Test_demultiplexing(TestCase):
    def setUp(self):
        self.xml_file1 = '../test_data/DemultiplexingStats.xml'
        self.xml_file2 = '../test_data/ConversionStats.xml'

    def test_parse_demultiplexing_stats(self):
        self.assertTrue(parse_demultiplexing_stats(self.xml_file1))

    def test_parse_conversion_stats(self):
        all_barcodes_per_lanes, top_unknown_barcodes_per_lanes = parse_conversion_stats(self.xml_file2)
        self.assertTrue(all_barcodes_per_lanes)
        self.assertTrue(top_unknown_barcodes_per_lanes)

    def test_demultiplexing_report(self):
        report = demultiplexing_report_wiki(self.xml_file2)
        self.assertTrue(report)
        print(report)

