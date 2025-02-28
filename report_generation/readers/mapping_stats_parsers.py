from collections import Counter
import csv
import yaml
import re

__author__ = 'tcezard'


def parse_bamtools_stats(bamtools_stats):
    """Parse the stat file generated by bamtools.
    :param bamtools_stats the text file generated by bamtools
    :return a tuple of 4 integers: total_reads, mapped_reads, duplicate_reads, proper_pairs
    """
    with open(bamtools_stats) as open_file:
        for line in open_file:
            sp_line = line.strip().split()
            if line.startswith('Total reads:'):
                total_reads = int(sp_line[2])
            elif line.startswith('Mapped reads:'):
                mapped_reads = int(sp_line[2])
            elif line.startswith('Duplicates:'):
                duplicate_reads = int(sp_line[1])
            elif line.startswith("'Proper-pairs':"):
                proper_pairs = int(sp_line[1])
    return total_reads, mapped_reads, duplicate_reads, proper_pairs



def parse_callable_bed_file(bed_file):
    """parse a bed file originating from GATK CallableLoci tool
    :param: bed_file the bed file generated by CallableLoci
    :return a dict containing the coverage value for each type of Loci"""
    coverage_per_type=Counter()
    with open(bed_file) as open_file:
        for line in open_file:
            sp_line = line.strip().split()
            coverage_per_type[sp_line[3]]+=int(sp_line[2]) - int(sp_line[1]) +1
    return coverage_per_type

def parse_highdepth_yaml_file(yaml_file):
    """parse a yaml file containing median coverage output by bcbio
    :param: yaml_file the bed file generated by CallableLoci
    :return a string representing the median coverage for that library"""
    content={}
    with open(yaml_file) as open_file:
        content = yaml.load(open_file)
    return content.get('median_cov', 0)

def parse_validate_csv(csv_file):
    snp_conc = indel_conc = snp_disc = indel_disc = 0
    with open(csv_file) as open_file:
        reader = csv.DictReader(open_file)
        for row in reader:
            if row.get('variant.type') == 'snp' and row.get('category') == 'concordant':
                snp_conc+=int(row.get('value'))
            elif row.get('variant.type') == 'indel' and row.get('category') == 'concordant':
                indel_conc+=int(row.get('value'))
            elif row.get('variant.type') == 'snp' and row.get('category') == 'discordant-extra-total':
                snp_disc+=int(row.get('value'))
            elif row.get('variant.type') == 'snp' and row.get('category') == 'discordant-shared-total':
                snp_disc+=int(row.get('value'))
            elif row.get('variant.type') == 'snp' and row.get('category') == 'discordant-missing-total':
                snp_disc+=int(row.get('value'))
            elif row.get('variant.type') == 'indel' and row.get('category') == 'discordant-extra-total':
                indel_disc+=int(row.get('value'))
            elif row.get('variant.type') == 'indel' and row.get('category') == 'discordant-shared-total':
                indel_disc+=int(row.get('value'))
            elif row.get('variant.type') == 'indel' and row.get('category') == 'discordant-missing-total':
                indel_disc+=int(row.get('value'))
    return snp_conc, indel_conc, snp_disc, indel_disc


def parse_genotype_concordance(genotype_concordance_file):
    lines = []
    with open(genotype_concordance_file) as open_file:
        inside = False
        for line in open_file:
            if not line.strip():
                inside = False
            if inside:
                lines.append(line)
            if line.startswith('#'):
                #header
                if 'GenotypeConcordance_Counts' in  line:
                    inside = True
    headers = lines[0].split()
    header_mapping = {}
    ignore_keys = []
    for key in headers:
        if key.endswith('UNAVAILABLE'):
            ignore_keys.append(key)
        elif key.endswith('NO_CALL') or key.endswith('MIXED'):
            header_mapping[key] = 'no_call_chip'
        elif key.startswith('NO_CALL') or key.startswith('UNAVAILABLE') or key.startswith('MIXED'):
            header_mapping[key] = 'no_call_seq'
        elif key[:int((len(key)-1)/2)] == key[int((len(key)+1)/2):]:
            header_mapping[key] = 'matching_snps'
        else:
            header_mapping[key] = 'mismatching_snps'

    samples = {}
    for sample_line in lines[1:]:
        sp_line = sample_line.split()
        sample_dict = Counter()
        for i in range(1, len(headers)):
            if headers[i] in header_mapping:
                sample_dict[header_mapping[headers[i]]] += int(sp_line[i])
        samples[sp_line[0]] = sample_dict
    return samples

def get_nb_sequence_from_fastqc_html(html_file):
    with open(html_file) as open_file:
        s = open_file.read()
        match = re.search('<td>Total Sequences</td><td>(\d+)</td>', s)
        if match:
            return int(match.group(1))
