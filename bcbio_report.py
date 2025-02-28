#!/usr/bin/env python
from argparse import ArgumentParser
import glob
import logging
import os
import re
from genologics.lims import Lims
from report_generation.config import Configuration
from report_generation.formaters import format_info
from report_generation.model import Info, ELEMENT_NB_READS_SEQUENCED, \
    ELEMENT_NB_MAPPED_READS, ELEMENT_NB_DUPLICATE_READS, ELEMENT_NB_PROPERLY_MAPPED, \
    ELEMENT_MEDIAN_COVERAGE, ELEMENT_PC_DUPLICATE_READS, ELEMENT_PC_PROPERLY_MAPPED, \
    ELEMENT_PC_BASES_CALLABLE, ELEMENT_SAMPLE_INTERNAL_ID, ELEMENT_SAMPLE_EXTERNAL_ID, ELEMENT_NB_READS_PASS_FILTER,\
    ELEMENT_PC_MAPPED_READS, ELEMENT_PROJECT, ELEMENT_YIELD, \
    ELEMENT_LIBRARY_INTERNAL_ID, ELEMENT_PC_Q30_R1, ELEMENT_PC_Q30_R2, ELEMENT_NB_BASE, ELEMENT_NB_READS_IN_BAM, \
    ELEMENT_MEAN_COVERAGE, ELEMENT_SAMPLE_PLATE, ELEMENT_SAMPLE_PLATE_WELL, ELEMENT_GENDER, ELEMENT_GENOTYPE_PC_NOCALL, \
    ELEMENT_GENOTYPE_PC_MISMATCH
from report_generation.readers.mapping_stats_parsers import parse_bamtools_stats, parse_callable_bed_file, \
    parse_highdepth_yaml_file, get_nb_sequence_from_fastqc_html, parse_genotype_concordance
from report_generation.rest_communication import post_entry, patch_entry

__author__ = 'tcezard'

cfg = Configuration()
lims=Lims(**cfg.get('clarity'))
female_alias = ['f', 'female']
male_alias = ['m', 'male']

def match_gender(gender1, gender2):
    gender1 = str(gender1).lower()
    gender2 = str(gender2).lower()
    if gender1.lower() in female_alias and gender2.lower() in female_alias:
        return  'female'
    elif gender1.lower() in male_alias and gender2.lower() in male_alias:
        return 'male'
    else:
        return 'mismatch (vcf:%s lims:%s)'%(gender1, gender2)

class Bcbio_report:
    headers = [ELEMENT_PROJECT, ELEMENT_SAMPLE_PLATE, ELEMENT_SAMPLE_PLATE_WELL, ELEMENT_SAMPLE_INTERNAL_ID, ELEMENT_SAMPLE_EXTERNAL_ID, ELEMENT_LIBRARY_INTERNAL_ID,
               ELEMENT_NB_READS_PASS_FILTER, ELEMENT_NB_READS_IN_BAM, ELEMENT_NB_MAPPED_READS, ELEMENT_PC_MAPPED_READS,
               ELEMENT_NB_DUPLICATE_READS, ELEMENT_PC_DUPLICATE_READS,
               ELEMENT_NB_PROPERLY_MAPPED, ELEMENT_PC_PROPERLY_MAPPED, ELEMENT_MEAN_COVERAGE,
               ELEMENT_PC_BASES_CALLABLE, ELEMENT_YIELD, ELEMENT_PC_Q30_R1, ELEMENT_PC_Q30_R2, ELEMENT_GENDER,
               ELEMENT_GENOTYPE_PC_NOCALL, ELEMENT_GENOTYPE_PC_MATCH]

    def __init__(self, bcbio_dirs):
        self.bcbio_dirs=bcbio_dirs
        self.all_info = []
        for bcbio_dir in self.bcbio_dirs:
            self.all_info.append(self._populate_lib_info(bcbio_dir))

    def _populate_lib_info(self, sample_dir):
        lib_info = Info()
        sample_dir = os.path.abspath(sample_dir)
        sample_name = os.path.basename(sample_dir)
        project_name = os.path.basename(os.path.dirname(sample_dir))
        lib_info[ELEMENT_SAMPLE_INTERNAL_ID]= sample_name
        lib_info[ELEMENT_LIBRARY_INTERNAL_ID]= sample_name
        lib_info[ELEMENT_PROJECT]= project_name
        plate, well = self.get_plate_id_and_well(sample_name)
        lib_info[ELEMENT_SAMPLE_PLATE] = plate
        lib_info[ELEMENT_SAMPLE_PLATE_WELL] = well
        fastq_file = glob.glob(os.path.join(sample_dir,"*_R1.fastq.gz"))[0]
        external_sample_name = os.path.basename(fastq_file)[:-len("_R1.fastq.gz")]
        lib_info[ELEMENT_SAMPLE_EXTERNAL_ID]= external_sample_name
        fastqc_file = os.path.join(sample_dir,external_sample_name+"_R1_fastqc.html")
        if os.path.exists(fastqc_file):
            nb_reads = get_nb_sequence_from_fastqc_html(fastqc_file)
            lib_info[ELEMENT_NB_READS_PASS_FILTER]= int(nb_reads)
            lib_info[ELEMENT_NB_BASE]= int(nb_reads)*300

        bamtools_path = glob.glob(os.path.join(sample_dir, 'bamtools_stats.txt'))
        if not bamtools_path:
            bamtools_path = glob.glob(os.path.join(sample_dir,'.qc', 'bamtools_stats.txt'))
        if bamtools_path:
            total_reads, mapped_reads, duplicate_reads, proper_pairs = parse_bamtools_stats(bamtools_path[0])
            lib_info[ELEMENT_NB_READS_IN_BAM]= int(total_reads)
            lib_info[ELEMENT_NB_MAPPED_READS]= int(mapped_reads)
            lib_info[ELEMENT_NB_DUPLICATE_READS]= int(duplicate_reads)
            lib_info[ELEMENT_NB_PROPERLY_MAPPED]= int(proper_pairs)

        yaml_metric_paths = glob.glob(os.path.join(sample_dir, '*%s-sort-highdepth-stats.yaml'%external_sample_name))
        if not yaml_metric_paths:
            yaml_metric_paths = glob.glob(os.path.join(sample_dir, '.qc', '*%s-sort-highdepth-stats.yaml'%external_sample_name))
        if yaml_metric_paths:
            yaml_metric_path = yaml_metric_paths[0]
            median_coverage  = parse_highdepth_yaml_file(yaml_metric_path)
            lib_info[ELEMENT_MEDIAN_COVERAGE]= median_coverage
        else:
            logging.critical('Missing %s-sort-highdepth-stats.yaml'%sample_name)

        bed_file_paths = glob.glob(os.path.join(sample_dir,'*%s-sort-callable.bed'%external_sample_name))
        if not bed_file_paths:
            bed_file_paths = glob.glob(os.path.join(sample_dir, '.qc', '*%s-sort-callable.bed'%external_sample_name))
        if bed_file_paths:
            bed_file_path = bed_file_paths[0]
            coverage_per_type = parse_callable_bed_file(bed_file_path)
            callable_bases = coverage_per_type.get('CALLABLE')
            total = sum(coverage_per_type.values())
            lib_info[ELEMENT_PC_BASES_CALLABLE]= callable_bases/total
        else:
            logging.critical('Missing *%s-sort-callable.bed'%sample_name)

        sex_file_paths = glob.glob(os.path.join(sample_dir,'%s.sex'%external_sample_name))
        if not sex_file_paths:
            sex_file_paths = glob.glob(os.path.join(sample_dir,'.qc','%s.sex'%external_sample_name))
        if sex_file_paths:
            with open(sex_file_paths[0]) as open_file:
                sex = open_file.read().strip()
                gender_from_lims = self.get_sex_from_lims(sample_name)
                lib_info[ELEMENT_GENDER]= match_gender(sex, gender_from_lims)
        genotype_file_paths = glob.glob(os.path.join(sample_dir,'%s_genotype_validation.txt'%external_sample_name))
        if genotype_file_paths:
            samples = parse_genotype_concordance(genotype_file_paths[0])
            total_snps = sum(samples[sample_name].values())
            no_call = samples[sample_name].get('no_call_seq') + samples[sample_name].get('no_call_chip')
            matching = samples[sample_name].get('matching_snps')
            lib_info[ELEMENT_GENOTYPE_PC_NOCALL] = float(no_call) / float(total_snps)
            lib_info[ELEMENT_GENOTYPE_PC_MISMATCH] = float(matching) / float(total_snps)
        return lib_info


    def get_plate_id_and_well(self, sample_name):
        samples = self.get_samples(sample_name)

        if len(samples) == 1:
            plate, well = samples[0].artifact.location
            return plate.name, well
        else:
            return None, None

    def get_samples(self, sample_name):
        samples = lims.get_samples(name=sample_name)
        if len(samples) == 0:
            sample_name_sub = re.sub("_(\d{2})",":\g<1>",sample_name)
            samples = lims.get_samples(name=sample_name_sub)
        if len(samples) == 0:
            sample_name_sub = re.sub("__(\w)_(\d{2})"," _\g<1>:\g<2>",sample_name)
            samples = lims.get_samples(name=sample_name_sub)
        return samples

    def get_sex_from_lims(self, sample_name):
        samples = self.get_samples(sample_name)
        if len(samples) == 1:
            gender = samples[0].udf.get('Gender')
            return gender



    def write_report_wiki(self):
        page_lines=[]
        page_lines.append('h1. Mapping Statistics')
        page_lines.extend(format_info(self.all_info, self.headers, style='wiki'))
        return '\n'.join(page_lines)

    def write_report_json(self):
        return format_info(self.all_info, self.headers, style='json')

    def send_data(self):

        cfg = Configuration()
        headers_samples = [ELEMENT_PROJECT, ELEMENT_LIBRARY_INTERNAL_ID, ELEMENT_SAMPLE_INTERNAL_ID,
                   ELEMENT_NB_READS_PASS_FILTER, ELEMENT_YIELD, ELEMENT_PC_Q30_R1, ELEMENT_PC_Q30_R2]
        array_json = format_info(self.all_info, headers_samples, style='array')
        url=cfg.query('rest_api','url') + 'samples/'
        for payload in array_json:
            if not post_entry(url, payload):
                id = payload.pop(ELEMENT_LIBRARY_INTERNAL_ID.key)
                patch_entry(url, payload, **{ELEMENT_LIBRARY_INTERNAL_ID.key:id})

    def __str__(self):
        return self.write_report_wiki()


def main():
    #Setup options
    argparser=_prepare_argparser()
    args = argparser.parse_args()
    if args.send_data:
        Bcbio_report(args.bcbio_dirs).send_data()
    elif args.style == 'wiki':
        print(Bcbio_report(args.bcbio_dirs).write_report_wiki())
    elif args.style == 'json':
        print(Bcbio_report(args.bcbio_dirs).write_report_json())

def _prepare_argparser():
    """Prepare optparser object. New arguments will be added in this
    function first.
    """
    description = """Simple script that parse bcbio outputs and generate a wiki table"""

    argparser = ArgumentParser(description=description)

    argparser.add_argument("-d", "--bcbio_dir", dest="bcbio_dirs", type=str, nargs='+',
                           help="The directories containing the bcbio data.")
    argparser.add_argument("--style", dest="style", type=str, help="The style of the report.", default='wiki')
    argparser.add_argument("--send_data", dest="send_data", action='store_true', default=False,
                           help="send data to the reporting app instead of printing the report.")
    return argparser


if __name__=="__main__":
    main()