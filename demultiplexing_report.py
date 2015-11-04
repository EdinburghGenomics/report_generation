#!/usr/bin/env python
from argparse import ArgumentParser
from collections import defaultdict, Counter
import xml.etree.ElementTree as ET
from report_generation.formaters import format_percent, format_info
from report_generation.model import Info, ELEMENT_PROJECT, ELEMENT_LIBRARY_INTERNAL_ID, ELEMENT_NB_READS_SEQUENCED, \
    ELEMENT_NB_READS_PASS_FILTER, ELEMENT_RUN_NAME, ELEMENT_LANE, ELEMENT_BARCODE, ELEMENT_NB_Q30_R1, ELEMENT_NB_BASE, \
    ELEMENT_NB_Q30_R2, ELEMENT_PC_PASS_FILTER, ELEMENT_PC_Q30_R1, ELEMENT_PC_Q30_R2, ELEMENT_PC_READ_IN_LANE, \
    ELEMENT_YIELD
from report_generation.readers.demultiplexing_parsers import parse_demultiplexing_stats, parse_conversion_stats

__author__ = 'tcezard'

class Demultiplexing_report:

    def __init__(self, xml_file):
        self._populate_barcode_info(xml_file)
        self._aggregate_data_per_library()
        self._aggregate_data_per_lane()


    def _aggregate_data_per_lane(self):
        self.lanes_info=defaultdict(Info)
        for barcode_info in self.barcodes_info:
            lane=barcode_info[ELEMENT_LANE]
            self.lanes_info[lane]+=barcode_info
        #add ELEMENT_PC_READ_IN_LANE to barcode info
        for barcode_info in self.barcodes_info:
            nb_reads_lane = self.lanes_info[barcode_info[ELEMENT_LANE]][ELEMENT_NB_READS_PASS_FILTER]
            barcode_info[ELEMENT_PC_READ_IN_LANE]=float(barcode_info[ELEMENT_NB_READS_PASS_FILTER])/float(nb_reads_lane)
        for barcode_info in self.unexpected_barcode_info:
            nb_reads_lane = self.lanes_info[barcode_info[ELEMENT_LANE]][ELEMENT_NB_READS_PASS_FILTER]
            barcode_info[ELEMENT_PC_READ_IN_LANE]=float(barcode_info[ELEMENT_NB_READS_PASS_FILTER])/float(nb_reads_lane)

    def _aggregate_data_per_library(self):
        self.libraries_info=defaultdict(Info)
        for barcode_info in self.barcodes_info:
            library=barcode_info[ELEMENT_LIBRARY_INTERNAL_ID]
            self.libraries_info[library]+=barcode_info

    def _populate_barcode_info(self, xml_file):
        all_barcodes_per_lanes, top_unknown_barcodes_per_lanes = parse_conversion_stats(xml_file)
        self.barcodes_info=[]
        for project, library, lane, barcode, clust_count, clust_count_pf, nb_bases,\
            nb_bases_r1q30, nb_bases_r2q30, in all_barcodes_per_lanes:
            barcode_info = Info()
            barcode_info[ELEMENT_PROJECT]=project
            barcode_info[ELEMENT_LIBRARY_INTERNAL_ID]=library
            barcode_info[ELEMENT_LANE]=lane
            barcode_info[ELEMENT_BARCODE]=barcode
            barcode_info[ELEMENT_NB_READS_SEQUENCED]=int(clust_count)
            barcode_info[ELEMENT_NB_READS_PASS_FILTER]=int(clust_count_pf)
            #For the paired end reads
            barcode_info[ELEMENT_NB_BASE]=int(nb_bases)*2
            barcode_info[ELEMENT_NB_Q30_R1]=int(nb_bases_r1q30)
            barcode_info[ELEMENT_NB_Q30_R2]=int(nb_bases_r2q30)
            self.barcodes_info.append(barcode_info)
        self.unexpected_barcode_info=[]
        for lane, barcode, clust_count in top_unknown_barcodes_per_lanes:
            barcode_info = Info()
            barcode_info[ELEMENT_LANE]=lane
            barcode_info[ELEMENT_BARCODE]=barcode
            barcode_info[ELEMENT_NB_READS_PASS_FILTER]=int(clust_count)
            self.unexpected_barcode_info.append(barcode_info)

    def _generate_lane_summary_table(self):
        headers = [ELEMENT_LANE, ELEMENT_PC_PASS_FILTER, ELEMENT_NB_READS_PASS_FILTER, ELEMENT_YIELD,
                   ELEMENT_PC_Q30_R1, ELEMENT_PC_Q30_R2]
        return format_info([self.lanes_info[lane] for lane in sorted(self.lanes_info)], headers)

    def _generate_sample_summary_table(self):
        headers = [ELEMENT_PROJECT, ELEMENT_LIBRARY_INTERNAL_ID, ELEMENT_BARCODE,
                   ELEMENT_NB_READS_PASS_FILTER, ELEMENT_YIELD, ELEMENT_PC_Q30_R1, ELEMENT_PC_Q30_R2]
        return format_info([self.libraries_info[library] for library in sorted(self.libraries_info)], headers)


    def _generate_sample_per_lane_table(self, lane):
        headers = [ELEMENT_LANE, ELEMENT_PC_PASS_FILTER, ELEMENT_PROJECT, ELEMENT_LIBRARY_INTERNAL_ID,
                  ELEMENT_BARCODE, ELEMENT_NB_READS_PASS_FILTER, ELEMENT_PC_READ_IN_LANE, ELEMENT_PC_Q30_R1,
                  ELEMENT_PC_Q30_R2]
        return format_info([barcode for barcode in self.barcodes_info if barcode[ELEMENT_LANE] == lane], headers)

    def _generate_demultiplexing_tab(self):
        tabbed_table=[]
        tabbed_table.append("{deck:id=demultiplexing}")
        for lane in sorted(self.lanes_info.keys()):
            tabbed_table.append("{card:label=Lane %s}"%lane)
            table = self._generate_sample_per_lane_table(lane)
            tabbed_table.extend(table)
            tabbed_table.append("{card}")
        tabbed_table.append("{deck}")

        return tabbed_table

    def _generate_unexpected_per_lane_table(self, lane):
        headers = [ELEMENT_LANE, ELEMENT_BARCODE, ELEMENT_NB_READS_PASS_FILTER, ELEMENT_PC_READ_IN_LANE]
        return format_info([barcode for barcode in self.unexpected_barcode_info if barcode[ELEMENT_LANE] == lane], headers)

    def _generate_unexpected_tab(self):
        tabbed_table=[]
        tabbed_table.append("{deck:id=unexpected}")
        for lane in sorted(self.lanes_info.keys()):
            tabbed_table.append("{card:label=Lane %s}"%lane)
            table = self._generate_unexpected_per_lane_table(lane)
            tabbed_table.extend(table)
            tabbed_table.append("{card}")
        tabbed_table.append("{deck}")

        return tabbed_table


    def write_report_wiki3(self):
        page_lines=[]
        page_lines.append("{composition-setup}{composition-setup}")
        page_lines.append("{deck:id=main_deck}")

        page_lines.append("{card:label=Summary per lane}")
        page_lines.append('h1. Summary per lane')
        page_lines.extend(self._generate_lane_summary_table())
        page_lines.append("{card}")

        page_lines.append("{card:label=Summary per library}")
        page_lines.append('h1. Summary per library')
        page_lines.extend(self._generate_sample_summary_table())
        page_lines.append("{card}")

        page_lines.append("{card:label=Demultiplexing}")
        page_lines.append('h1. Demultiplexing results')
        page_lines.extend(self._generate_demultiplexing_tab())
        page_lines.append("{card}")

        page_lines.append("{card:label=Unexpected barcodes}")
        page_lines.append('h1. Unexpected barcodes results')
        page_lines.extend(self._generate_unexpected_tab())
        page_lines.append("{card}")

        page_lines.append("{deck}")
        return '\n'.join(page_lines)

    def write_report_wiki(self):
        page_lines=[]
        page_lines.append("{toc}")
        page_lines.append('h1. Summary per lane')
        page_lines.extend(self._generate_lane_summary_table())

        page_lines.append('h1. Summary per library')
        page_lines.extend(self._generate_sample_summary_table())

        page_lines.append('h1. Demultiplexing results')
        page_lines.extend(self._generate_demultiplexing_tab())

        page_lines.append('h1. Unexpected barcodes results')
        page_lines.extend(self._generate_unexpected_tab())

        return '\n'.join(page_lines)


    def __str__(self):
        return self.write_report_wiki()

def main():
    #Setup options
    argparser=_prepare_argparser()
    args = argparser.parse_args()
    print(Demultiplexing_report(args.xml_file))

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