from report_generation.formaters import default_formatter, format_longint, format_percent, format_float, link_page

__author__ = 'tcezard'

class Piece_of_info():
    """Define the header and formatter for a piece of information"""
    def __init__(self, key, text=None, formatter=default_formatter, formula=None):
        self.key = key
        if text:
            self.text=text
        else:
            self.text=key
        self.formatter = formatter
        self.formula=formula

    def __repr__(self):
        return self.text

    __str__ = __repr__

def extract_data(info, key1, key2):
    val1=val2=None
    if isinstance(key1, Piece_of_info):
        val1 = info.get(key1, None)
    else:
        val1 = key1
    if isinstance(key2, Piece_of_info):
        val2 = info.get(key2, None)
    else:
        val2 = key2
    return val1, val2

def divide(info, key1, key2):
    val1, val2 = extract_data(info, key1, key2)
    if val1 and val2 and val2!=0:
        return float(val1)/float(val2)
    else:
        return ''

def multiply(info, key1, key2):
    val1, val2 = extract_data(info, key1, key2)
    if val1 and val2:
        return float(val1)*float(val2)
    else:
        return ''

def add(info, key1, key2):
    val1, val2 = extract_data(info, key1, key2)
    if val1 and val2:
        return float(val1)+float(val2)
    else:
        return ''

def substract(info, key1, key2):
    val1, val2 = extract_data(info, key1, key2)
    if val1 and val2:
        return float(val1)-float(val2)
    else:
        return ''


ELEMENT_RUN_ELEMENT_ID = Piece_of_info(
    key='run_element_id',
    text=None,
    formatter=default_formatter
)
ELEMENT_PROJECT = Piece_of_info(
    key='project',
    text='Project',
    formatter=default_formatter
)
ELEMENT_SAMPLE_PLATE = Piece_of_info(
    key='plate',
    text='Plate Id',
    formatter=default_formatter
)
ELEMENT_SAMPLE_PLATE_WELL = Piece_of_info(
    key='well',
    text='Well',
    formatter=default_formatter
)
ELEMENT_LIBRARY_INTERNAL_ID = Piece_of_info(
    key='library_id',
    text='Library LIMS id',
    formatter=default_formatter
)
ELEMENT_SAMPLE_INTERNAL_ID = Piece_of_info(
    key='sample_id',
    text='Sample LIMS id',
    formatter=default_formatter
)
ELEMENT_SAMPLE_EXTERNAL_ID = Piece_of_info(
    key='user_sample_id',
    text='User id',
    formatter=default_formatter
)
ELEMENT_NB_READS_SEQUENCED = Piece_of_info(
    key='read_sequenced',
    text='Nb of reads',
    formatter=format_longint
)
ELEMENT_NB_READS_PASS_FILTER = Piece_of_info(
    key='passing_filter_reads',
    text='Passing filter reads',
    formatter=format_longint
)
ELEMENT_NB_READS_IN_BAM = Piece_of_info(
    key='reads_in_bam',
    text='Nb reads in bam',
    formatter=format_longint
)
ELEMENT_PC_PASS_FILTER = Piece_of_info(
    key='pc_pass_filter',
    text='%PF',
    formatter=format_percent,
    formula=[divide, ELEMENT_NB_READS_PASS_FILTER, ELEMENT_NB_READS_SEQUENCED]
)
ELEMENT_NB_MAPPED_READS = Piece_of_info(
    key='nb_mapped_reads',
    text='Nb mapped reads',
    formatter=format_longint
)
ELEMENT_PC_MAPPED_READS = Piece_of_info(
    key='pc_mapped_reads',
    text='% mapped reads',
    formatter=format_percent,
    formula=[divide, ELEMENT_NB_MAPPED_READS, ELEMENT_NB_READS_IN_BAM]
)
ELEMENT_NB_SEC_MAPPED_READS = Piece_of_info(
    key='Nb secondary alignments',
    formatter=format_longint
)
ELEMENT_PC_SEC_MAPPED_READS = Piece_of_info(
    key='% secondary alignments',
    formatter=format_percent,
    formula=[divide, ELEMENT_NB_SEC_MAPPED_READS, ELEMENT_NB_READS_IN_BAM]
)
ELEMENT_NB_DUPLICATE_READS = Piece_of_info(
    key='nb_duplicate_reads',
    text='Nb duplicate reads',
    formatter=format_longint
)
ELEMENT_PC_DUPLICATE_READS = Piece_of_info(
    key='pc_duplicate_reads',
    text='% duplicate reads',
    formatter=format_percent,
    formula=[divide, ELEMENT_NB_DUPLICATE_READS, ELEMENT_NB_MAPPED_READS]
)
ELEMENT_NB_PROPERLY_MAPPED = Piece_of_info(
    key='nb_properly_mapped_reads',
    text='Nb properly mapped reads',
    formatter=format_longint
)
ELEMENT_PC_PROPERLY_MAPPED = Piece_of_info(
    key='pc_properly_mapped_reads',
    text='% properly mapped reads',
    formatter=format_percent,
    formula=[divide, ELEMENT_NB_PROPERLY_MAPPED, ELEMENT_NB_MAPPED_READS]
)
ELEMENT_MEDIAN_INSERT_SIZE = Piece_of_info(
    key='Median Insert Size',
    formatter=format_float
)
ELEMENT_LIBRARY_MEAN_INSERT_SIZE = Piece_of_info(
    key='Mean Insert Size',
    formatter=format_longint
)
ELEMENT_LIBRARY_STDDEV_INSERT_SIZE = Piece_of_info(
    key='Std dev Insert Size',
    formatter=format_longint
)
ELEMENT_MEDIAN_COVERAGE = Piece_of_info(
    key='median_coverage',
    text='Median coverage',
    formatter=format_longint
)
ELEMENT_NB_BASES_CALLABLE = Piece_of_info(
    key='Callable',
    formatter=format_longint
)
ELEMENT_PC_BASES_CALLABLE = Piece_of_info(
    key='pc_callable',
    text='%Callable',
    formatter=format_percent
)
ELEMENT_NB_BASES_NO_COVERAGE = Piece_of_info(
    key='No_Coverage',
    formatter=format_longint
)
ELEMENT_NB_BASES_LOW_COVERAGE = Piece_of_info(
    key='Low_Coverage',
    formatter=format_longint
)
ELEMENT_NB_BASES_EXCESS_COVERAGE = Piece_of_info(
    key='Excess_Coverage',
    formatter=format_longint
)
ELEMENT_NB_BASES_POOR_QUALITY = Piece_of_info(
    key='Poor_Quality',
    formatter=format_longint
)
ELEMENT_NB_BASES_10X = Piece_of_info(
    key='Nb bases 10X cov',
    formatter=format_longint
)
ELEMENT_PC_BASES_10X = Piece_of_info(
    key='% bases 10X cov',
    formatter=format_percent
)
ELEMENT_NB_BASES_30X = Piece_of_info(
    key='Nb bases 30X cov',
    formatter=format_longint
)
ELEMENT_PC_BASES_30X = Piece_of_info(
    key='% bases 30X cov',
    formatter=format_percent
)
ELEMENT_NB_SNP_CONCORDANT = Piece_of_info(
    key='Nb SNPs concordant',
    formatter=format_longint
)
ELEMENT_PC_SNP_CONCORDANT = Piece_of_info(
    key='% SNPs concordant',
    formatter=format_percent
)
ELEMENT_NB_INDEL_CONCORDANT = Piece_of_info(
    key='Nb Indels concordant',
    formatter=format_longint
)
ELEMENT_PC_INDEL_CONCORDANT = Piece_of_info(
    key='% Indels concordant',
    formatter=format_percent
)
ELEMENT_RUN_NAME = Piece_of_info(
    key='run_id',
    text='Run name',
    formatter=default_formatter
)
ELEMENT_LANE = Piece_of_info(
    key = 'lane',
    text='Lane',
    formatter=default_formatter
)
ELEMENT_BARCODE = Piece_of_info(
    key='barcode',
    text='Barcode',
    formatter=default_formatter
)
ELEMENT_NB_BASE_R1 = Piece_of_info(
    key='Nb bases in read 1',
    formatter=format_longint
)
ELEMENT_NB_BASE_R2 = Piece_of_info(
    key='Nb bases in read 2',
    formatter=format_longint
)
ELEMENT_NB_BASE = Piece_of_info(
    key='Nb bases',
    formatter=format_longint,
    formula=[add, ELEMENT_NB_BASE_R1, ELEMENT_NB_BASE_R2]
)
ELEMENT_NB_MAPPING_BASE = Piece_of_info(
    key='Nb mapping bases',
    formatter=format_longint,
    formula=[multiply, ELEMENT_NB_BASE, ELEMENT_PC_MAPPED_READS]
)
ELEMENT_NB_DUPLICATE_BASE = Piece_of_info(
    key='Nb duplicate bases',
    formatter=format_longint,
    formula=[multiply, ELEMENT_NB_MAPPING_BASE, ELEMENT_PC_DUPLICATE_READS]
)
ELEMENT_NB_UNIQUE_BASE = Piece_of_info(
    key='Nb unique bases',
    formatter=format_longint,
    formula=[substract, ELEMENT_NB_MAPPING_BASE, ELEMENT_NB_DUPLICATE_BASE]
)
ELEMENT_MEAN_COVERAGE = Piece_of_info(
    key='Mean coverage',
    formatter=format_float,
    formula=[divide, ELEMENT_NB_UNIQUE_BASE, 3217346917]
)
ELEMENT_NB_Q30_R1 = Piece_of_info(
    key='nb_q30_r1',
    text='Nb bases Q30 R1',
    formatter=format_longint
)
ELEMENT_NB_Q30_R2 = Piece_of_info(
    key='nb_q30_r2',
    text='Nb bases Q30 R2',
    formatter=format_longint
)
ELEMENT_NB_Q30 = Piece_of_info(
    key='pc_q30',
    text='Nb bases Q30',
    formatter=format_longint,
    formula=[add, ELEMENT_NB_Q30_R1, ELEMENT_NB_Q30_R2]
)
ELEMENT_PC_Q30 = Piece_of_info(
    key='pc_q30',
    text='%Q30',
    formatter=format_percent,
    formula=[divide, ELEMENT_NB_Q30,ELEMENT_NB_BASE]
)
ELEMENT_PC_Q30_R1 = Piece_of_info(
    key='pc_q30_r1',
    text='%Q30 R1',
    formatter=format_percent,
    formula=[divide, ELEMENT_NB_Q30_R1,ELEMENT_NB_BASE_R1])

ELEMENT_PC_Q30_R2 = Piece_of_info(
    key='pc_q30_r2',
    text='%Q30 R2',
    formatter=format_percent,
    formula=[divide, ELEMENT_NB_Q30_R2,ELEMENT_NB_BASE_R2]
)
ELEMENT_YIELD = Piece_of_info(
    key='yield_in_gb',
    text='Yield Gb',
    formatter=format_float,
    formula=[divide, ELEMENT_NB_BASE, 1000000000]
)
ELEMENT_PC_READ_IN_LANE = Piece_of_info(
    key='pc_reads_in_lane',
    text='%read in lane',
    formatter=format_percent
)
ELEMENT_LANE_COEFF_VARIATION = Piece_of_info(
    key='lane_coeff_variation',
    text='CV',
    formatter=format_float
)
ELEMENT_GENDER = Piece_of_info(
    key='gender',
    text='Gender',
    formatter=default_formatter
)
ALL_PIECES=[
    ELEMENT_RUN_ELEMENT_ID, ELEMENT_PROJECT, ELEMENT_LIBRARY_INTERNAL_ID, ELEMENT_SAMPLE_INTERNAL_ID,
    ELEMENT_SAMPLE_EXTERNAL_ID, ELEMENT_NB_READS_SEQUENCED, ELEMENT_NB_READS_PASS_FILTER,
    ELEMENT_NB_READS_IN_BAM, ELEMENT_PC_PASS_FILTER, ELEMENT_NB_MAPPED_READS, ELEMENT_PC_MAPPED_READS,
    ELEMENT_NB_SEC_MAPPED_READS, ELEMENT_PC_SEC_MAPPED_READS, ELEMENT_NB_DUPLICATE_READS,
    ELEMENT_PC_DUPLICATE_READS, ELEMENT_NB_PROPERLY_MAPPED, ELEMENT_PC_PROPERLY_MAPPED,
    ELEMENT_MEDIAN_INSERT_SIZE, ELEMENT_LIBRARY_MEAN_INSERT_SIZE, ELEMENT_LIBRARY_STDDEV_INSERT_SIZE,
    ELEMENT_MEDIAN_COVERAGE, ELEMENT_NB_BASES_CALLABLE, ELEMENT_PC_BASES_CALLABLE, ELEMENT_NB_BASES_NO_COVERAGE,
    ELEMENT_NB_BASES_LOW_COVERAGE, ELEMENT_NB_BASES_EXCESS_COVERAGE, ELEMENT_NB_BASES_POOR_QUALITY,
    ELEMENT_NB_BASES_10X, ELEMENT_PC_BASES_10X, ELEMENT_NB_BASES_30X, ELEMENT_PC_BASES_30X,
    ELEMENT_NB_SNP_CONCORDANT, ELEMENT_PC_SNP_CONCORDANT, ELEMENT_NB_INDEL_CONCORDANT,
    ELEMENT_PC_INDEL_CONCORDANT, ELEMENT_RUN_NAME, ELEMENT_LANE, ELEMENT_BARCODE, ELEMENT_NB_BASE_R1,
    ELEMENT_NB_BASE_R2, ELEMENT_NB_BASE, ELEMENT_NB_MAPPING_BASE, ELEMENT_NB_DUPLICATE_BASE,
    ELEMENT_NB_UNIQUE_BASE, ELEMENT_MEAN_COVERAGE, ELEMENT_NB_Q30_R1, ELEMENT_NB_Q30_R2,
    ELEMENT_NB_Q30, ELEMENT_PC_Q30, ELEMENT_PC_Q30_R1, ELEMENT_PC_Q30_R2, ELEMENT_YIELD,
    ELEMENT_PC_READ_IN_LANE, ELEMENT_LANE_COEFF_VARIATION
]

class Info:
    """"""
    def __init__(self):
        self._info={}

    def __setitem__(self, key, value):
        if isinstance(key,Piece_of_info):
            self._info[key]=value
        else:
            raise ValueError("Only instances of Piece_of_info can be used as Key")

    def __getitem__(self, key):
        if isinstance(key,Piece_of_info):
            return self._info.get(key)
        else:
            raise ValueError("Only instances of Piece_of_info can be used as Key")

    def get(self, key, *args, **kwargs):
        #Get the info stored
        value = self._info.get(key, None)
        #or get the info through formula
        if not value and key.formula:
            value = key.formula[0](self, *key.formula[1:])
        #or get the info through the passed default value
        if not value:
            value = self._info.get(key, *args, **kwargs)
        return value

    def __contains__(self, item):
        return item in self._info

    def __iter__(self):
        return self._info.__iter__()

    def format_line(self, keys=None, style=None):
        if keys is None:
            keys=self._info.keys()
        out = []
        for key in keys:
            value = self.get(key)
            if value is None:
                value = ''
            out.append(key.formatter(value, style=style))
        return out


    def format_line_wiki(self, keys=None):
        return '| %s |'%(' | '.join(self.format_line(keys, style="wiki")))

    def format_entry_dict(self, headers, style):
        return dict(zip([h.key for h in headers], self.format_line(headers, style)))

    def __add__(self, other):
        new_info = Info()
        for key in set(self).union(set(other)):
            if key in self  and key in other:
                if key.formatter in [format_longint, format_float]:
                    new_info[key] = self[key] + other[key]
                elif self[key] == other[key]:
                    new_info[key] = self[key]
                else:
                    join_char = '-'
                    tmp = set(str(self[key]).split(join_char)).union(set(str(other[key]).split(join_char)))
                    new_info[key] = join_char.join(tmp)
            elif key in other:
                new_info[key]=other[key]
            else:
                new_info[key]=self[key]
        return new_info

    def __radd__(self, other):
        return self.__add__(other)

