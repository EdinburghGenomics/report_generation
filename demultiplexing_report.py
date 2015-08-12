#!/usr/bin/env python
from argparse import ArgumentParser
from collections import defaultdict, Counter
import xml.etree.ElementTree as ET
from report_generation.readers.demultiplexing_parsers import parse_demultiplexing_stats, parse_conversion_stats

__author__ = 'tcezard'


class Demultiplexing_report:

    def __init__(self, xml_file):
        self.all_barcodes_per_lanes, self.top_unknown_barcodes_per_lanes = parse_conversion_stats(xml_file)
        self._aggregate_data_per_lane()

    def _aggregate_data_per_lane(self):
        self.data_per_lane=defaultdict(dict)
        for project, library, lane, barcode, clust_count, clust_count_pf, nb_bases, nb_bases_r1q30, nb_bases_r2q30, in self.all_barcodes_per_lanes:
            self.data_per_lane[lane][barcode]=(project, library, clust_count, clust_count_pf, nb_bases, nb_bases_r1q30, nb_bases_r2q30)
            if not 'total' in self.data_per_lane[lane]:
                self.data_per_lane[lane]['total']=0
            self.data_per_lane[lane]['total']+=clust_count


    def _generate_demultiplexing_table(self):
        table=[]
        table.append('|| %s ||'%' || '.join(['Lane','Project', 'Library', 'Barcode', 'Nb of Read', '% of Read', 'Yield (Gb)', '%Q30 R1', '%Q30 R1']))

        for lane in sorted(self.data_per_lane.keys()):
            #get the total number of read for that lane
            clust_count_total = self.data_per_lane.get(lane).get('total')
            for barcode in self.data_per_lane.get(lane):
                if barcode=='total':
                    continue
                line=[]
                project, library, clust_count, clust_count_pf, nb_bases, nb_bases_r1q30, nb_bases_r2q30 = self.data_per_lane.get(lane).get(barcode)
                line.append(lane)
                line.append(project)
                line.append(library)
                line.append(barcode)
                line.append(str(clust_count_pf))
                line.append('%.2f%%'%(float(clust_count_pf)/float(clust_count_total)*100))
                line.append('%.2f'%(float(nb_bases)/1000000000))
                line.append('%.2f%%'%(float(nb_bases_r1q30)/float(nb_bases)*100))
                line.append('%.2f%%'%(float(nb_bases_r2q30)/float(nb_bases)*100))
                table.append('| %s |'%' | '.join(line))
        return table

    def _generate_unexpected_barcodes_table(self):
        table = []
        table.append('|| %s ||'%' || '.join(['Lane', 'Barcode', 'Nb of Read', '% of Unexpected', '% of Lane']))
        for lane, barcode, clust_count in self.top_unknown_barcodes_per_lanes:
            clust_count_total = self.data_per_lane.get(lane).get('total')
            d, d, clust_count_unknown, clust_count_pf_unknown, d,d,d = self.data_per_lane.get(lane).get('unknown')
            if barcode.startswith('NNNNNN'):
                clust_count = int(clust_count) - (int(clust_count_unknown) - int(clust_count_pf_unknown))
            line = []
            line.append(lane)
            line.append(barcode)
            line.append(str(clust_count))
            line.append('%.2f%%'%(float(clust_count)/float(clust_count_pf_unknown)*100))
            line.append('%.2f%%'%(float(clust_count)/float(clust_count_total)*100))
            table.append('| %s |'%' | '.join(line))
        return table

    def write_report_wiki(self):
        page_lines=[]
        page_lines.append('h1. Demultiplexing results')
        page_lines.extend(self._generate_demultiplexing_table())
        page_lines.append('h1. Unexpected barcodes results')
        page_lines.extend(self._generate_unexpected_barcodes_table())
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