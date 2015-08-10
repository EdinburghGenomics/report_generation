#!/usr/bin/env python
from argparse import ArgumentParser
from collections import defaultdict, Counter
import xml.etree.ElementTree as ET
from report_generation.readers.demultiplexing_parsers import parse_demultiplexing_stats, parse_conversion_stats

__author__ = 'tcezard'

def demultiplexing_report_wiki(xml_file):
    all_barcodes_per_lanes, top_unknown_barcodes_per_lanes = parse_conversion_stats(xml_file)
    data_per_lane=defaultdict(dict)
    for project, library, lane, barcode, clust_count, clust_count_pf, nb_bases, nb_bases_r1q30, nb_bases_r2q30, in all_barcodes_per_lanes:
        data_per_lane[lane][barcode]=(project, library, clust_count, clust_count_pf, nb_bases, nb_bases_r1q30, nb_bases_r2q30)
        if not 'total' in data_per_lane[lane]:
            data_per_lane[lane]['total']=0
        data_per_lane[lane]['total']+=clust_count
    table=[]
    table.append('|| %s ||'%' || '.join(['Lane','Project', 'Library', 'Barcode', 'Nb of Read', '% of Read', 'Yield (Gb)', '%Q30 R1', '%Q30 R1']))
    for lane in sorted(data_per_lane.keys()):
        #get the total number of read for that lane
        clust_count_total = data_per_lane.get(lane).get('total')
        for barcode in data_per_lane.get(lane):
            if barcode=='total':
                continue
            line=[]
            project, library, clust_count, clust_count_pf, nb_bases, nb_bases_r1q30, nb_bases_r2q30 = data_per_lane.get(lane).get(barcode)
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
    return '\n'.join(table)




def main():
    #Setup options
    argparser=_prepare_argparser()
    args = argparser.parse_args()
    print(demultiplexing_report_wiki(args.xml_file))

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