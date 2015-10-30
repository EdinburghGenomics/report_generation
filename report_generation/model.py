from report_generation.formaters import default_formatter, format_longint, format_percent, format_float, link_page

__author__ = 'tcezard'

class Piece_of_info():
    """Define the header and formatter for a piece of information"""
    def __init__(self, key, formatter=default_formatter, formula=None):
        self.key = key
        self.formatter = formatter
        self.formula=formula

    def __repr__(self):
        return  self.key

    __str__ = __repr__

def divide(info, key1, key2):
    val1=val2=None
    if isinstance(key1, int) or isinstance(key1, float):
        val1 = key1
    elif info[key1]:
        val1 = info[key1]
    if isinstance(key2, int) or isinstance(key2, float):
        val2 = key2
    elif info[key2]:
        val2 = info[key2]
    if val1 and val2 and val2!=0:
        return float(val1)/float(val2)
    else:
        return 'nan'

ELEMENT_PROJECT = Piece_of_info(key='Project', formatter=default_formatter)
ELEMENT_LIBRARY_INTERNAL_ID = Piece_of_info(key='LIMS Id', formatter=default_formatter)
ELEMENT_LIBRARY_EXTERNAL_ID = Piece_of_info(key='External Id', formatter=default_formatter)
ELEMENT_NB_READS_SEQUENCED = Piece_of_info(key='Nb of reads', formatter=format_longint)
ELEMENT_NB_READS_PASS_FILTER = Piece_of_info(key='Passing filter reads', formatter=format_longint)
ELEMENT_PC_PASS_FILTER = Piece_of_info(key='%PF', formatter=format_percent,
                                       formula=[divide, ELEMENT_NB_READS_PASS_FILTER,ELEMENT_NB_READS_SEQUENCED])
ELEMENT_NB_MAPPED_READS = Piece_of_info(key='Nb mapped reads', formatter=format_longint)
ELEMENT_PC_MAPPED_READS = Piece_of_info(key='% mapped reads', formatter=format_percent,
                                        formula=[divide, ELEMENT_NB_MAPPED_READS, ELEMENT_NB_READS_PASS_FILTER])
ELEMENT_NB_SEC_MAPPED_READS = Piece_of_info(key='Nb secondary alignments', formatter=format_longint)
ELEMENT_PC_SEC_MAPPED_READS = Piece_of_info(key='% secondary alignments', formatter=format_percent,
                                            formula=[divide, ELEMENT_NB_SEC_MAPPED_READS, ELEMENT_NB_READS_PASS_FILTER])
ELEMENT_NB_DUPLICATE_READS = Piece_of_info(key='Nb duplicate reads', formatter=format_longint)
ELEMENT_PC_DUPLICATE_READS = Piece_of_info(key='% duplicate reads', formatter=format_percent,
                                           formula=[divide, ELEMENT_NB_DUPLICATE_READS, ELEMENT_NB_READS_PASS_FILTER])
ELEMENT_NB_PROPERLY_MAPPED = Piece_of_info(key='Nb properly mapped reads', formatter=format_longint)
ELEMENT_PC_PROPERLY_MAPPED = Piece_of_info(key='% properly mapped reads', formatter=format_percent,
                                           formula=[divide, ELEMENT_NB_PROPERLY_MAPPED, ELEMENT_NB_READS_PASS_FILTER])
ELEMENT_MEDIAN_INSERT_SIZE = Piece_of_info(key='Median Insert Size', formatter=format_float)
ELEMENT_LIBRARY_MEAN_INSERT_SIZE = Piece_of_info(key='Mean Insert Size', formatter=format_longint)
ELEMENT_LIBRARY_STDDEV_INSERT_SIZE = Piece_of_info(key='Std dev Insert Size', formatter=format_longint)
ELEMENT_MEAN_COVERAGE = Piece_of_info(key='Mean coverage', formatter=format_float)
ELEMENT_MEDIAN_COVERAGE = Piece_of_info(key='Median coverage', formatter=format_longint)
ELEMENT_NB_BASES_CALLABLE = Piece_of_info(key='Callable', formatter=format_longint)
ELEMENT_PC_BASES_CALLABLE = Piece_of_info(key='%Callable', formatter=format_percent)
ELEMENT_NB_BASES_NO_COVERAGE = Piece_of_info(key='No_Coverage', formatter=format_longint)
ELEMENT_NB_BASES_LOW_COVERAGE = Piece_of_info(key='Low_Coverage', formatter=format_longint)
ELEMENT_NB_BASES_EXCESS_COVERAGE = Piece_of_info(key='Excess_Coverage', formatter=format_longint)
ELEMENT_NB_BASES_POOR_QUALITY = Piece_of_info(key='Poor_Quality', formatter=format_longint)
ELEMENT_NB_BASES_10X = Piece_of_info(key='Nb bases 10X cov', formatter=format_longint)
ELEMENT_PC_BASES_10X = Piece_of_info(key='% bases 10X cov', formatter=format_percent)
ELEMENT_NB_BASES_30X = Piece_of_info(key='Nb bases 30X cov', formatter=format_longint)
ELEMENT_PC_BASES_30X = Piece_of_info(key='% bases 30X cov', formatter=format_percent)
ELEMENT_NB_SNP_CONCORDANT = Piece_of_info(key='Nb SNPs concordant', formatter=format_longint)
ELEMENT_PC_SNP_CONCORDANT = Piece_of_info(key='% SNPs concordant', formatter=format_percent)
ELEMENT_NB_INDEL_CONCORDANT = Piece_of_info(key='Nb Indels concordant', formatter=format_longint)
ELEMENT_PC_INDEL_CONCORDANT = Piece_of_info(key='% Indels concordant', formatter=format_percent)
ELEMENT_RUN_NAME = Piece_of_info(key='Run name', formatter=default_formatter)
ELEMENT_LANE = Piece_of_info(key='Lane', formatter=default_formatter)
ELEMENT_BARCODE = Piece_of_info(key='Barcode', formatter=default_formatter)
ELEMENT_NB_BASE = Piece_of_info(key='Nb bases', formatter=format_longint)
ELEMENT_NB_Q30_R1 = Piece_of_info(key='Nb bases Q30 R1', formatter=format_longint)
ELEMENT_NB_Q30_R2 = Piece_of_info(key='Nb bases Q30 R2', formatter=format_longint)
ELEMENT_PC_Q30_R1 = Piece_of_info(key='%Q30 R1', formatter=format_percent,
                                  formula=[divide, ELEMENT_NB_Q30_R1,ELEMENT_NB_BASE])
ELEMENT_PC_Q30_R2 = Piece_of_info(key='%Q30 R2', formatter=format_percent,
                                  formula=[divide, ELEMENT_NB_Q30_R2,ELEMENT_NB_BASE])
ELEMENT_YIELD = Piece_of_info(key='Yield Gb', formatter=format_float,
                                  formula=[divide, ELEMENT_NB_BASE, 1000000000])
ELEMENT_PC_READ_IN_LANE = Piece_of_info(key='%read in lane', formatter=format_percent)

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

    def __contains__(self, item):
        return item in self._info

    def __iter__(self):
        return self._info.__iter__()

    def format_line(self, keys, style=None):
        out = []
        for key in keys:
            value = self._info.get(key, None)
            if not value and key.formula:
                value = key.formula[0](self, *key.formula[1:])
            if not value:
                value='NA'
            out.append(key.formatter(value, style=style))
        return out

    def format_line_wiki(self, keys):
        return '| %s |'%(' | '.join(self.format_line(keys, style="wiki")))

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
                    tmp = set(self[key].split(join_char)).union(set(other[key].split(join_char)))
                    new_info[key] = join_char.join(tmp)
            elif key in other:
                new_info[key]=other[key]
            else:
                new_info[key]=self[key]
        return new_info

    def __radd__(self, other):
        return self.__add__(other)

