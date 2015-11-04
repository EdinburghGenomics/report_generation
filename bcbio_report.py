#!/usr/bin/env python
from argparse import ArgumentParser
import glob
import logging
import os
from report_generation.formaters import format_longint, format_percent, format_float
from report_generation.model import Info, ELEMENT_LIBRARY_EXTERNAL_ID, ELEMENT_NB_READS_SEQUENCED, \
    ELEMENT_NB_MAPPED_READS, ELEMENT_NB_DUPLICATE_READS, ELEMENT_NB_PROPERLY_MAPPED, \
    ELEMENT_MEDIAN_COVERAGE, ELEMENT_NB_SNP_CONCORDANT, ELEMENT_PC_SNP_CONCORDANT, \
    ELEMENT_NB_INDEL_CONCORDANT, ELEMENT_PC_INDEL_CONCORDANT, ELEMENT_PC_MAPPED_READS, \
    ELEMENT_PC_DUPLICATE_READS, ELEMENT_PC_PROPERLY_MAPPED, ELEMENT_PC_BASES_CALLABLE, ELEMENT_SAMPLE_INTERNAL_ID, \
    ELEMENT_SAMPLE_EXTERNAL_ID
from report_generation.readers.mapping_stats_parsers import parse_bamtools_stats, parse_callable_bed_file, \
    parse_highdepth_yaml_file, parse_validate_csv

__author__ = 'tcezard'


class Bcbio_report:

    def __init__(self, bcbio_dirs):
        self.bcbio_dirs=bcbio_dirs

    def _populate_lib_info(self, sample_dir):
        lib_info = Info()

        sample_name = os.path.basename(sample_dir)
        lib_info[ELEMENT_SAMPLE_INTERNAL_ID]= sample_name
        fastq_file = glob.glob(os.path.join(sample_dir,"*_R1.fastq.gz"))[0]
        external_sample_name = os.path.basename(fastq_file)[:-len("_R1.fastq.gz")]
        lib_info[ELEMENT_SAMPLE_EXTERNAL_ID]= external_sample_name

        bamtools_path = os.path.join(sample_dir, 'bamtools_stats.txt')
        total_reads, mapped_reads, duplicate_reads, proper_pairs = parse_bamtools_stats(bamtools_path)
        lib_info[ELEMENT_NB_READS_SEQUENCED]= total_reads
        lib_info[ELEMENT_NB_MAPPED_READS]= mapped_reads
        lib_info[ELEMENT_NB_DUPLICATE_READS]= duplicate_reads
        lib_info[ELEMENT_NB_PROPERLY_MAPPED]= proper_pairs

        yaml_metric_paths = glob.glob(os.path.join(sample_dir, '%s-sort-highdepth-stats.yaml'%sample_name))
        if yaml_metric_paths:
            yaml_metric_path = yaml_metric_paths[0]
            median_coverage  = parse_highdepth_yaml_file(yaml_metric_path)
            lib_info[ELEMENT_MEDIAN_COVERAGE]= median_coverage

        bed_file_paths = glob.glob(os.path.join(sample_dir,'*%s-sort-callable.bed'%sample_name))
        if bed_file_paths:
            bed_file_path = bed_file_paths[0]
            coverage_per_type = parse_callable_bed_file(bed_file_path)
            callable_bases = coverage_per_type.get('CALLABLE')
            total = sum(coverage_per_type.values())
            lib_info[ELEMENT_PC_BASES_CALLABLE]= callable_bases/total

        return lib_info

    def _write_mapping_stats_report(self):
        headers = [ELEMENT_LIBRARY_EXTERNAL_ID, ELEMENT_NB_READS_SEQUENCED,ELEMENT_NB_MAPPED_READS,
                     ELEMENT_NB_DUPLICATE_READS, ELEMENT_PC_DUPLICATE_READS, ELEMENT_NB_PROPERLY_MAPPED,
                     ELEMENT_PC_PROPERLY_MAPPED, ELEMENT_MEDIAN_COVERAGE, ELEMENT_PC_BASES_CALLABLE]
        table = []
        table.append('|| %s ||' % (' || '.join([str(h) for h in headers])))
        for bcbio_dir in self.bcbio_dirs:
            lib_info = self._populate_lib_info(bcbio_dir)
            if lib_info:
                lib_info.format_line(headers)
                table.append(lib_info.format_line_wiki(headers))
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
    elif len(paths)>1:
        logging.error('More than one library found in {}'.format(bcbio_dir))
        return None
    else:
        logging.error('No library found in {}'.format(bcbio_dir))
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