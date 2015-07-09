#!/usr/bin/env python
from argparse import ArgumentParser
from collections import defaultdict
import xml.etree.ElementTree as ET

__author__ = 'tcezard'


def demultiplexing_report_wiki(xml_file):
    parsed_data = parse_demultiplexing_stats(xml_file)
    data_per_lane=defaultdict(dict)
    for project, library, barcode, lane, barcode_count in parsed_data:
        data_per_lane[lane][barcode]=(project, library, barcode_count)
    table=[]
    table.append('|| %s ||'%' || '.join(['Lane','Project', 'Library', 'Barcode', 'Nb of Read', '% of Read']))
    for lane in sorted(data_per_lane.keys()):
        #get the total number of read for that lane
        project, library, barcode_count_total = data_per_lane.get(lane).get('all')
        assigned_barcodes=0
        for barcode in data_per_lane.get(lane):
            if barcode=='all':
                continue
            line=[]
            project, library, barcode_count = data_per_lane.get(lane).get(barcode)
            line.append(lane)
            line.append(project)
            line.append(library)
            line.append(barcode)
            line.append(barcode_count)
            line.append('%.2f%%'%(float(barcode_count)/float(barcode_count_total)*100))
            assigned_barcodes += int(barcode_count)
            table.append('| %s |'%' | '.join(line))
        line=[]
        unassigned_barcode = int(barcode_count_total)-assigned_barcodes
        line.append(lane)
        line.append('')
        line.append('')
        line.append('unknown')
        line.append(str(unassigned_barcode))
        line.append('%.2f%%'%(float(unassigned_barcode)/float(barcode_count_total)*100))
        table.append('| %s |'%' | '.join(line))
        line=[]
        line.append(lane)
        line.append('')
        line.append('')
        line.append('Total')
        line.append(str(barcode_count_total))
        line.append('%.2f%%'%(float(barcode_count_total)/float(barcode_count_total)*100))
        table.append('|| %s ||'%' || '.join(line))
    return '\n'.join(table)

def parse_demultiplexing_stats(xml_file):
    """parse the demultiplexing_stats.xml to extract number of read for each barcodes"""
    tree = ET.parse(xml_file).getroot()
    all_elements = []
    for project in tree.iter('Project'):
        if project.get('name') == 'default': continue
        for sample in project.findall('Sample'):
            for barcode in sample.findall('Barcode'):
                if project.get('name') != 'all' and barcode.get('name') == 'all': continue
                for lane in barcode.findall('Lane'):
                    all_elements.append((project.get('name'), sample.get('name'), barcode.get('name'), lane.get('number'), lane.find('BarcodeCount').text))
    return all_elements


from unittest import TestCase

class Test_demultiplexing(TestCase):

    def setUp(self):
        self.xml_file = 'test_data/DemultiplexingStats.xml'

    def test_parse_demultiplexing_stats(self):
        self.assertTrue(parse_demultiplexing_stats(self.xml_file))

    def test_demultiplexing_report_wiki(self):
        self.assertTrue(demultiplexing_report_wiki(self.xml_file))


def main():
    #Setup options
    argparser=_prepare_argparser()
    args = argparser.parse_args()
    print demultiplexing_report_wiki(args.xml_file)


def _prepare_argparser():
    """Prepare optparser object. New arguments will be added in this
    function first.
    """
    description = """Simple script that parse demultiplexed xml file and generate an wiki table"""

    argparser = ArgumentParser(description=description)

    argparser.add_argument("-x", "--xml-file", dest="xml_file", type=str, help="The demultiplexed_Stats.xml to parse.")
    return argparser


if __name__=="__main__":
    main()