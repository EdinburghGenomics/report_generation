#!/usr/bin/env python
from argparse import ArgumentParser
from collections import defaultdict, Counter
import glob
import os
import xml.etree.ElementTree as ET
from report_generation.readers.demultiplexing_parsers import parse_demultiplexing_stats, parse_conversion_stats
from report_generation.readers.mapping_stats_parsers import parse_bamtools_stats, parse_callable_bed_file

__author__ = 'tcezard'


class Bcbio_report:

    def __init__(self, bcbio_dirs):
        self.bcbio_dirs=bcbio_dirs


    def _write_mapping_stats_report(self):
        table = []
        header = ['Library Id', 'Reads in Bam', 'Reads mapped', 'Duplicated reads', 'Proper pair reads', '%callable bases']
        table.append('|| %s ||'%' || '.join(header))
        for bcbio_dir in self.bcbio_dirs:
            line = []
            lib_name = get_library_name_from_dir(bcbio_dir)
            bamtools_path = os.path.join(bcbio_dir,'final', lib_name, 'qc','bamtools', 'bamtools_stats.txt')
            total_reads, mapped_reads, duplicate_reads, proper_pairs = parse_bamtools_stats(bamtools_path)
            line.append(lib_name)
            line.append(str(total_reads))
            line.append(str(mapped_reads))
            line.append(str(duplicate_reads))
            line.append(str(proper_pairs))
            bed_file_path = os.path.join(bcbio_dir,'work', 'align', lib_name,'%s-sort-callable.bed'%lib_name)
            coverage_per_type = parse_callable_bed_file(bed_file_path)
            callable_bases = coverage_per_type.get('CALLABLE')
            total = sum(coverage_per_type.values())
            line.append('%.2f%%'%(callable_bases/total))
            table.append('| %s |'%' | '.join(line))
        return table

    def write_report_wiki(self):
        page_lines=[]
        page_lines.append('h1. Mapping Statistics')
        page_lines.extend(self._write_mapping_stats_report())
        return '\n'.join(page_lines)


    def __str__(self):
        return self.write_report_wiki()

def get_library_name_from_dir(bcbio_dir):
    paths = glob.glob(os.path.join(bcbio_dir,'final','*','qc'))
    if paths and len(paths)==1:
        return os.path.basename(os.path.dirname(paths[0]))
    else:
        return None

def main():
    #Setup options
    argparser=_prepare_argparser()
    args = argparser.parse_args()
    print(Bcbio_report(args.bcbio_dirs))

def _prepare_argparser():
    """Prepare optparser object. New arguments will be added in this
    function first.
    """
    description = """Simple script that parse bcbio outputs and generate a wiki table"""

    argparser = ArgumentParser(description=description)

    argparser.add_argument("-d", "--bcbio_dir", dest="bcbio_dirs", type=str, nargs='+', help="The directories containing the bcbio data.")
    return argparser


if __name__=="__main__":
    main()