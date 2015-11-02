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
    ELEMENT_PC_DUPLICATE_READS, ELEMENT_PC_PROPERLY_MAPPED, ELEMENT_PC_BASES_CALLABLE
from report_generation.readers.mapping_stats_parsers import parse_bamtools_stats, parse_callable_bed_file, \
    parse_highdepth_yaml_file, parse_validate_csv

__author__ = 'tcezard'


class Bcbio_report:

    def __init__(self, bcbio_dirs):
        self.bcbio_dirs=bcbio_dirs

    def _populate_lib_info(self, bcbio_dir):
        lib_info = Info()
        lib_name = get_library_name_from_dir(bcbio_dir)
        if lib_name is None:
            return None

        bamtools_path = os.path.join(bcbio_dir,'final', lib_name, 'qc','bamtools', 'bamtools_stats.txt')
        total_reads, mapped_reads, duplicate_reads, proper_pairs = parse_bamtools_stats(bamtools_path)
        lib_info[ELEMENT_LIBRARY_EXTERNAL_ID]= lib_name
        lib_info[ELEMENT_NB_READS_SEQUENCED]= total_reads
        lib_info[ELEMENT_NB_MAPPED_READS]= mapped_reads
        lib_info[ELEMENT_NB_DUPLICATE_READS]= duplicate_reads
        lib_info[ELEMENT_NB_PROPERLY_MAPPED]= proper_pairs

        yaml_metric_paths = glob.glob(os.path.join(bcbio_dir,'work', 'align', lib_name,'*%s-sort-highdepth-stats.yaml'%lib_name))
        if yaml_metric_paths:
            yaml_metric_path = yaml_metric_paths[0]
            median_coverage  = parse_highdepth_yaml_file(yaml_metric_path)
            lib_info[ELEMENT_MEDIAN_COVERAGE]= median_coverage

        bed_file_paths = glob.glob(os.path.join(bcbio_dir,'work', 'align', lib_name,'*%s-sort-callable.bed'%lib_name))
        if bed_file_paths:
            bed_file_path = bed_file_paths[0]
            coverage_per_type = parse_callable_bed_file(bed_file_path)
            callable_bases = coverage_per_type.get('CALLABLE')
            total = sum(coverage_per_type.values())
            lib_info[ELEMENT_PC_BASES_CALLABLE]= callable_bases/total

        validation_files = glob.glob(os.path.join(bcbio_dir,'final', '*-merged', 'grading-summary-%s-joint.csv'%lib_name))
        if len(validation_files) == 1:
            snp_conc, indel_conc, snp_disc, indel_disc = parse_validate_csv(validation_files[0])
            lib_info[ELEMENT_NB_SNP_CONCORDANT]= snp_conc
            lib_info[ELEMENT_PC_SNP_CONCORDANT]= snp_conc/float(snp_conc+snp_disc)
            lib_info[ELEMENT_NB_INDEL_CONCORDANT]= indel_conc
            lib_info[ELEMENT_PC_INDEL_CONCORDANT]= indel_conc/float(indel_conc+indel_disc)
        return lib_info

    def _write_mapping_stats_report(self):
        headers = [ELEMENT_LIBRARY_EXTERNAL_ID, ELEMENT_NB_READS_SEQUENCED,ELEMENT_NB_MAPPED_READS,
                     ELEMENT_NB_DUPLICATE_READS, ELEMENT_PC_DUPLICATE_READS, ELEMENT_NB_PROPERLY_MAPPED,
                     ELEMENT_PC_PROPERLY_MAPPED, ELEMENT_MEDIAN_COVERAGE, ELEMENT_PC_BASES_CALLABLE,
                     ELEMENT_NB_SNP_CONCORDANT, ELEMENT_PC_SNP_CONCORDANT, ELEMENT_NB_INDEL_CONCORDANT,
                     ELEMENT_PC_INDEL_CONCORDANT]
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