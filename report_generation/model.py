from report_generation.formaters import default_formatter, format_longint, format_percent, format_float, link_page

__author__ = 'tcezard'

class Piece_of_info():
    def __init__(self, key, formatter):
        self.key = key
        self.formatter = formatter

    def __repr__(self):
        return  self.key

    __str__ = __repr__


LIBRARY_ELEMENT_PROJECT = Piece_of_info(key='Project', formatter=default_formatter)
LIBRARY_ELEMENT_INTERNAL_ID = Piece_of_info(key='Internal Id', formatter=default_formatter)
LIBRARY_ELEMENT_EXTERNAL_ID = Piece_of_info(key='Internal Id', formatter=default_formatter)
LIBRARY_ELEMENT_NB_READS_SEQUENCED = Piece_of_info(key='Nb of reads', formatter=format_longint)
LIBRARY_ELEMENT_NB_READS_PASS_FILTER = Piece_of_info(key='Passing filter reads', formatter=format_longint)
LIBRARY_ELEMENT_NB_MAPPED_READS = Piece_of_info(key='Nb mapped reads', formatter=format_longint)
LIBRARY_ELEMENT_PC_MAPPED_READS = Piece_of_info(key='% mapped reads', formatter=format_percent)
LIBRARY_ELEMENT_NB_SEC_MAPPED_READS = Piece_of_info(key='Nb secondary alignments', formatter=format_longint)
LIBRARY_ELEMENT_PC_SEC_MAPPED_READS = Piece_of_info(key='% secondary alignments', formatter=format_percent)
LIBRARY_ELEMENT_NB_DUPLICATE_READS = Piece_of_info(key='Nb duplicate reads', formatter=format_longint)
LIBRARY_ELEMENT_PC_DUPLICATE_READS = Piece_of_info(key='% duplicate reads', formatter=format_percent)
LIBRARY_ELEMENT_NB_PROPERLY_MAPPED = Piece_of_info(key='Nb properly mapped reads', formatter=format_longint)
LIBRARY_ELEMENT_PC_PROPERLY_MAPPED = Piece_of_info(key='% properly mapped reads', formatter=format_percent)
LIBRARY_ELEMENT_MEDIAN_INSERT_SIZE = Piece_of_info(key='Median Insert Size', formatter=format_float)
LIBRARY_ELEMENT_MEAN_INSERT_SIZE = Piece_of_info(key='Mean Insert Size', formatter=format_longint)
LIBRARY_ELEMENT_STDDEV_INSERT_SIZE = Piece_of_info(key='Std dev Insert Size', formatter=format_longint)
LIBRARY_ELEMENT_IS_PLOT = Piece_of_info(key='Insert Size plot', formatter=link_page)
LIBRARY_ELEMENT_MEAN_COVERAGE = Piece_of_info(key='Mean coverage', formatter=format_float)
LIBRARY_ELEMENT_MEDIAN_COVERAGE = Piece_of_info(key='Median coverage', formatter=format_longint)
LIBRARY_ELEMENT_NB_BASES_CALLABLE = Piece_of_info(key='Callable', formatter=format_longint)
LIBRARY_ELEMENT_PC_BASES_CALLABLE = Piece_of_info(key='%Callable', formatter=format_percent)
LIBRARY_ELEMENT_NB_BASES_NO_COVERAGE = Piece_of_info(key='No_Coverage', formatter=format_longint)
LIBRARY_ELEMENT_NB_BASES_LOW_COVERAGE = Piece_of_info(key='Low_Coverage', formatter=format_longint)
LIBRARY_ELEMENT_NB_BASES_EXCESS_COVERAGE = Piece_of_info(key='Excess_Coverage', formatter=format_longint)
LIBRARY_ELEMENT_NB_BASES_POOR_QUALITY = Piece_of_info(key='Poor_Quality', formatter=format_longint)
LIBRARY_ELEMENT_NB_BASES_10X = Piece_of_info(key='Nb bases 10X cov', formatter=format_longint)
LIBRARY_ELEMENT_PC_BASES_10X = Piece_of_info(key='% bases 10X cov', formatter=format_percent)
LIBRARY_ELEMENT_NB_BASES_30X = Piece_of_info(key='Nb bases 30X cov', formatter=format_longint)
LIBRARY_ELEMENT_PC_BASES_30X = Piece_of_info(key='% bases 30X cov', formatter=format_percent)
LIBRARY_ELEMENT_NB_SNP_CONCORDANT = Piece_of_info(key='Nb SNPs concordant', formatter=format_longint)
LIBRARY_ELEMENT_PC_SNP_CONCORDANT = Piece_of_info(key='% SNPs concordant', formatter=format_percent)
LIBRARY_ELEMENT_NB_INDEL_CONCORDANT = Piece_of_info(key='Nb Indels concordant', formatter=format_longint)
LIBRARY_ELEMENT_PC_INDEL_CONCORDANT = Piece_of_info(key='% Indels concordant', formatter=format_percent)

class Library_info:

    def __init__(self):
        self.info={}

    def __setitem__(self, key, value):
        self.info[key]=value

    def format_line(self, keys, style=None):
        out = []
        for key in keys:
            if key in self.info:
                out.append(key.formatter(self.info.get(key), style=style))
            else:
                out.append('NA')
        return out

    def format_line_wiki(self, keys):
        return '| %s |'%(' | '.join(self.format_line(keys, style="wiki")))
