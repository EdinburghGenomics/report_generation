#!/usr/bin/env python
from argparse import ArgumentParser
from collections import defaultdict
import os
from report_generation.config import Configuration
from report_generation.formaters import format_percent, format_info
from report_generation.model import Info, ELEMENT_PROJECT, ELEMENT_LIBRARY_INTERNAL_ID, ELEMENT_NB_READS_SEQUENCED, \
    ELEMENT_NB_READS_PASS_FILTER, ELEMENT_RUN_NAME, ELEMENT_LANE, ELEMENT_BARCODE, ELEMENT_NB_Q30_R1, ELEMENT_NB_BASE, \
    ELEMENT_NB_Q30_R2, ELEMENT_PC_PASS_FILTER, ELEMENT_PC_Q30_R1, ELEMENT_PC_Q30_R2, ELEMENT_PC_READ_IN_LANE, \
    ELEMENT_YIELD, ELEMENT_SAMPLE_INTERNAL_ID, ELEMENT_ID, ELEMENT_NB_BASE_R1, \
    ELEMENT_NB_BASE_R2, ELEMENT_LANE_COEFF_VARIATION, ELEMENT_PC_Q30
from report_generation.readers.demultiplexing_parsers import parse_conversion_stats
from scipy.stats import variation
from report_generation.readers.sample_sheet import SampleSheet
from report_generation.rest_communication import post_entry, patch_entry

__author__ = 'tcezard'


class Demultiplexing_report:

    def __init__(self, run_dir, conversion_xml_file):
        self.run_id = os.path.basename(os.path.abspath(run_dir))

        self.headers_barcodes = [ELEMENT_RUN_NAME, ELEMENT_LANE, ELEMENT_PC_PASS_FILTER, ELEMENT_PROJECT,
                                 ELEMENT_LIBRARY_INTERNAL_ID, ELEMENT_SAMPLE_INTERNAL_ID, ELEMENT_BARCODE,
                                 ELEMENT_NB_READS_PASS_FILTER, ELEMENT_PC_READ_IN_LANE, ELEMENT_YIELD,
                                 ELEMENT_PC_Q30_R1, ELEMENT_PC_Q30_R2]
        self.headers_lane = [ELEMENT_RUN_NAME, ELEMENT_LANE, ELEMENT_PC_PASS_FILTER, ELEMENT_NB_READS_PASS_FILTER,
                             ELEMENT_YIELD, ELEMENT_PC_Q30, ELEMENT_PC_Q30_R1, ELEMENT_PC_Q30_R2,
                             ELEMENT_LANE_COEFF_VARIATION]
        self.headers_samples = [ELEMENT_PROJECT, ELEMENT_LIBRARY_INTERNAL_ID, ELEMENT_SAMPLE_INTERNAL_ID, ELEMENT_BARCODE,
                   ELEMENT_NB_READS_PASS_FILTER, ELEMENT_YIELD, ELEMENT_PC_Q30_R1, ELEMENT_PC_Q30_R2]
        self.headers_unexpected = [ELEMENT_RUN_NAME, ELEMENT_LANE, ELEMENT_BARCODE, ELEMENT_NB_READS_PASS_FILTER, ELEMENT_PC_READ_IN_LANE]

        self._populate_barcode_info_from_SampleSheet(run_dir)
        if conversion_xml_file:
            self._populate_barcode_info_from_conversion_file(conversion_xml_file)
        self._aggregate_data_per_library()
        self._aggregate_data_per_lane()

    def _aggregate_data_per_lane(self):
        self.lanes_info=defaultdict(Info)
        for barcode_info in self.barcodes_info.values():
            lane=barcode_info[ELEMENT_LANE]
            self.lanes_info[lane]+=barcode_info
        #add ELEMENT_PC_READ_IN_LANE to barcode info
        for barcode_info in self.barcodes_info.values():
            nb_reads_lane = self.lanes_info[barcode_info[ELEMENT_LANE]][ELEMENT_NB_READS_PASS_FILTER]
            if nb_reads_lane:
                barcode_info[ELEMENT_PC_READ_IN_LANE]=float(barcode_info[ELEMENT_NB_READS_PASS_FILTER])/float(nb_reads_lane)
            else:
                barcode_info[ELEMENT_PC_READ_IN_LANE]=''

        #add ELEMENT_LANE_COEFF_VARIATION to lane_info
        nb_reads_per_lane = defaultdict(list)
        for barcode_info in self.barcodes_info.values():
            if barcode_info[ELEMENT_BARCODE] != 'unknown' and barcode_info[ELEMENT_NB_READS_PASS_FILTER]:
                nb_reads_per_lane[barcode_info[ELEMENT_LANE]].append(barcode_info[ELEMENT_NB_READS_PASS_FILTER])
        for lane in self.lanes_info:
            if nb_reads_per_lane.get(lane):
                self.lanes_info[lane][ELEMENT_LANE_COEFF_VARIATION] = variation(nb_reads_per_lane.get(lane))

        #add ELEMENT_PC_READ_IN_LANE to barcode info
        for barcode_info in self.unexpected_barcode_info.values():
            nb_reads_lane = self.lanes_info[barcode_info[ELEMENT_LANE]][ELEMENT_NB_READS_PASS_FILTER]
            if nb_reads_lane:
                barcode_info[ELEMENT_PC_READ_IN_LANE]=float(barcode_info[ELEMENT_NB_READS_PASS_FILTER])/float(nb_reads_lane)
            else:
                barcode_info[ELEMENT_PC_READ_IN_LANE]=''

    def _aggregate_data_per_library(self):
        self.libraries_info=defaultdict(Info)
        for barcode_info in self.barcodes_info.values():
            library=barcode_info[ELEMENT_LIBRARY_INTERNAL_ID]
            self.libraries_info[library]+=barcode_info

    def _populate_barcode_info_from_SampleSheet(self, run_dir):
        self.barcodes_info={}
        samplesheet = SampleSheet(run_dir)
        for project_id, proj_obj in samplesheet.sample_projects.items():
            for sample_id_obj in proj_obj.sample_ids.values():
                for sample in sample_id_obj.samples:
                    for lane in sample.lane.split('+'):
                        barcode_info = Info()
                        barcode_info[ELEMENT_BARCODE]=sample.barcode
                        barcode_info[ELEMENT_ID] = '%s_%s_%s'%(self.run_id, lane, sample.barcode)
                        barcode_info[ELEMENT_RUN_NAME]=self.run_id
                        barcode_info[ELEMENT_PROJECT]=project_id
                        barcode_info[ELEMENT_SAMPLE_INTERNAL_ID]=sample.sample_id
                        barcode_info[ELEMENT_LIBRARY_INTERNAL_ID]=sample.sample_name
                        barcode_info[ELEMENT_LANE]=lane
                        self.barcodes_info[barcode_info[ELEMENT_ID]]=(barcode_info)

                        barcode_info = Info()
                        barcode_info[ELEMENT_BARCODE]='unknown'
                        barcode_info[ELEMENT_ID] = '%s_%s_%s'%(self.run_id, lane, 'unknown')
                        barcode_info[ELEMENT_RUN_NAME]=self.run_id
                        barcode_info[ELEMENT_PROJECT] = 'default'
                        barcode_info[ELEMENT_SAMPLE_INTERNAL_ID]='Undetermined'
                        barcode_info[ELEMENT_LIBRARY_INTERNAL_ID]='Undetermined'
                        barcode_info[ELEMENT_LANE]=lane
                        self.barcodes_info[barcode_info[ELEMENT_ID]]=(barcode_info)
        self.unexpected_barcode_info={}

    def _populate_barcode_info_from_conversion_file(self, conversion_xml_file):
        all_barcodes_per_lanes, top_unknown_barcodes_per_lanes = parse_conversion_stats(conversion_xml_file)
        for project, library, lane, barcode, clust_count, clust_count_pf, nb_bases,\
            nb_bases_r1q30, nb_bases_r2q30, in all_barcodes_per_lanes:
            barcode_info = self.barcodes_info.get('%s_%s_%s'%(self.run_id, lane, barcode))
            barcode_info[ELEMENT_NB_READS_SEQUENCED]=int(clust_count)
            barcode_info[ELEMENT_NB_READS_PASS_FILTER]=int(clust_count_pf)
            #For the paired end reads
            barcode_info[ELEMENT_NB_BASE_R1]=int(nb_bases)
            barcode_info[ELEMENT_NB_BASE_R2]=int(nb_bases)
            barcode_info[ELEMENT_NB_Q30_R1]=int(nb_bases_r1q30)
            barcode_info[ELEMENT_NB_Q30_R2]=int(nb_bases_r2q30)

        for lane, barcode, clust_count in top_unknown_barcodes_per_lanes:
            barcode_info = Info()
            barcode_info[ELEMENT_ID] = '%s_%s_%s'%(self.run_id, lane, barcode)
            barcode_info[ELEMENT_RUN_NAME]=self.run_id
            barcode_info[ELEMENT_LANE]=lane
            barcode_info[ELEMENT_BARCODE]=barcode
            barcode_info[ELEMENT_NB_READS_PASS_FILTER]=int(clust_count)
            self.unexpected_barcode_info[barcode_info[ELEMENT_ID]]=(barcode_info)

    def _generate_lane_summary_table(self):
        return format_info([self.lanes_info[lane] for lane in sorted(self.lanes_info)], self.headers_lane)

    def _generate_sample_summary_table(self):
        return format_info([self.libraries_info[library] for library in sorted(self.libraries_info)], self.headers_samples)

    def _generate_sample_per_lane_table(self, lane):
        return format_info([barcode for barcode in self.barcodes_info.values() if barcode[ELEMENT_LANE] == lane], self.headers_barcodes)

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
        return format_info([barcode for barcode in self.unexpected_barcode_info.values() if barcode[ELEMENT_LANE] == lane], self.headers_unexpected)

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

    def write_report_json(self):
        return format_info(self.all_info, self.headers, style='json')

    def send_data(self):
        headers_barcodes = [ELEMENT_ID, ELEMENT_RUN_NAME, ELEMENT_LANE, ELEMENT_PC_PASS_FILTER, ELEMENT_PROJECT,
                                 ELEMENT_LIBRARY_INTERNAL_ID, ELEMENT_SAMPLE_INTERNAL_ID, ELEMENT_BARCODE,
                                 ELEMENT_NB_READS_PASS_FILTER, ELEMENT_PC_READ_IN_LANE, ELEMENT_YIELD,
                                 ELEMENT_PC_Q30_R1, ELEMENT_PC_Q30_R2]
        headers_samples = [ELEMENT_PROJECT, ELEMENT_LIBRARY_INTERNAL_ID, ELEMENT_SAMPLE_INTERNAL_ID,
                   ELEMENT_NB_READS_PASS_FILTER, ELEMENT_YIELD, ELEMENT_PC_Q30_R1, ELEMENT_PC_Q30_R2]
        headers_unexpected = [ELEMENT_ID, ELEMENT_RUN_NAME, ELEMENT_LANE, ELEMENT_BARCODE, ELEMENT_NB_READS_PASS_FILTER, ELEMENT_PC_READ_IN_LANE]

        cfg = Configuration()
        #Send run elements
        headers=[ELEMENT_ID]
        headers.extend(self.headers_barcodes)
        array_json = format_info(self.barcodes_info.values(), headers_barcodes, style='array')
        url=cfg.query('rest_api','url') + 'run_elements/'
        for payload in array_json:
            if not post_entry(url, payload):
                id = payload.pop(ELEMENT_ID.key)
                patch_entry(url, payload, **{ELEMENT_ID.key:id})

        array_json = format_info(self.libraries_info.values(), headers_samples, style='array')
        url=cfg.query('rest_api','url') + 'samples/'
        for payload in array_json:
            if not post_entry(url, payload):
                id = payload.pop(ELEMENT_LIBRARY_INTERNAL_ID.key)
                patch_entry(url, payload, **{ELEMENT_LIBRARY_INTERNAL_ID.key:id})

        #Send unexpected barcodes
        array_json = format_info(self.unexpected_barcode_info.values(), headers_unexpected, style='array')
        url=cfg.query('rest_api','url') + 'unexpected_barcodes/'
        for payload in array_json:
            if not post_entry(url, payload):
                id = payload.pop(ELEMENT_ID.key)
                patch_entry(url, payload, **{ELEMENT_ID.key:id})



    def __str__(self):
        return self.write_report_wiki()

def main():
    #Setup options
    argparser=_prepare_argparser()
    args = argparser.parse_args()
    r = Demultiplexing_report(args.run_dir, args.conversion_xml)
    if args.send_data:
        r.send_data()
    elif args.style == 'wiki':
        print(r.write_report_wiki())
    elif args.style == 'json':
        print(r.write_report_json())

def _prepare_argparser():
    """Prepare optparser object. New arguments will be added in this
    function first.
    """
    description = """Simple script that parse demultiplexed xml file and generate an wiki table"""

    argparser = ArgumentParser(description=description)
    argparser.add_argument("-c", "--conversion_xml-file", dest="conversion_xml", type=str, help="The ConversionStats.xml to parse.")
    argparser.add_argument("-r", "--run_dir", dest="run_dir", type=str, help="The directory containing the SampleSheet.csv of the Run.")
    argparser.add_argument("--style", dest="style", type=str, help="The style of the report.", default='wiki')
    argparser.add_argument("--send_data", dest="send_data", action='store_true', default=False, help="send data to the reporting app instead of printing the report.")

    return argparser


if __name__=="__main__":
    main()
