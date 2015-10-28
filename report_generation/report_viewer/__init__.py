__author__ = 'mwham'
import flask as fl
from collections import defaultdict
import requests

DEBUG = False

app = fl.Flask(__name__)
app.config.from_object(__name__)


@app.route('/')
def main_page():
    return fl.render_template('main.html')

@app.route('/report/<run_id>')
def report(run_id):
    data = _get_reports(run_id)
    print(data)
    tables = defaultdict(list)
    for entry in data['_items']:
        report_type = entry['report_type']
        tables[report_type].append(entry['payload'])
    print(tables)
    return fl.render_template('report.html', run_id=run_id, tables=tables)


def _get_reports(run_id):
    query = requests.get('http://127.0.0.1:5002/analysis_driver_reports?where=run_id=="{run_id}"'.format(run_id=run_id))
    return query.json()


if __name__ == '__main__':
    app.run('localhost', 5000)

x = {
    'demultiplexing_results': [
        {
            'Reads': '50%',
            'Library': 'LP600-35523',
            'Q30_R1': '15',
            'Yield_in_Gb': '4',
            'Barcode': 'ATGCGCGT',
            'PF': '13.2%',
            'Nb_of_Reads': '1337',
            'Lane': '2'
        },
        {
            'Reads': '50%',
            'Library': 'LP600-35523',
            'Q30_R1': '15',
            'Yield_in_Gb': '4',
            'Barcode': 'ATGCGCGT',
            'PF': '13.2%',
            'Nb_of_Reads': '1337',
            'Lane': '2'
        },
        {
            'Reads': '50%',
            'Library': 'LP600-35523',
            'Q30_R1': '15',
            'Yield_in_Gb': '4',
            'Barcode': 'ATGCGCGT',
            'PF': '13.2%',
            'Nb_of_Reads': '1337',
            'Lane': '2'
        },
        {
            'Reads': '50%',
            'Library': 'LP600-35523',
            'Q30_R1': '15',
            'Yield_in_Gb': '4',
            'Barcode': 'ATGCGCGT',
            'PF': '13.2%',
            'Nb_of_Reads': '1337',
            'Lane': '2'
        },
        {
            'Unexpected': '10%',
            'Barcode': 'ATGCGCGT',
            'of_Lane': '5%',
            'Nb_of_Reads': '13',
            'Lane': '2'
        },
        {
            'Reads': '50%',
            'Library': 'LP600-35523',
            'Q30_R1': '15',
            'Yield_in_Gb': '4',
            'Barcode': 'ATGCGCGT',
            'PF': '13.2%',
            'Nb_of_Reads': '1337',
            'Lane': '2'
        }
    ],
    'bcbio_report': [
        {
            'properly_mapped_reads': '97.12%',
            'Nb_SNPs_concordant': 'NA',
            'duplicate_reads': '7.74%',
            'Nb_of_reads': '8,241,917',
            'Median_coverage': '20.312',
            'Nb_mapped_reads': '8,123,798',
            'SNPs_concordant': 'NA',
            'Internal_ID': 'MD13046',
            'Indels_concordant': 'NA',
            'Nb_properly_mapped_reads': '7,889,705',
            'Nb_duplicate_reads': '628,559',
            'Nb_Indels_concordant': 'NA',
            'Callable': '0.31%'
        },
        {
            'properly_mapped_reads': '97.12%',
            'Nb_SNPs_concordant': 'NA',
            'duplicate_reads': '7.74%',
            'Nb_of_reads': '8,241,917',
            'Median_coverage': '20.312',
            'Nb_mapped_reads': '8,123,798',
            'SNPs_concordant': 'NA',
            'Internal_ID': 'MD13046',
            'Indels_concordant': 'NA',
            'Nb_properly_mapped_reads': '7,889,705',
            'Nb_duplicate_reads': '628,559',
            'Nb_Indels_concordant': 'NA',
            'Callable': '0.31%'
        },
        {
            'properly_mapped_reads': '97.12%',
            'Nb_SNPs_concordant': 'NA',
            'duplicate_reads': '7.74%',
            'Nb_of_reads': '8,241,917',
            'Median_coverage': '20.312',
            'Nb_mapped_reads': '8,123,798',
            'SNPs_concordant': 'NA',
            'Internal_ID': 'MD13046',
            'Indels_concordant': 'NA',
            'Nb_properly_mapped_reads': '7,889,705',
            'Nb_duplicate_reads': '628,559',
            'Nb_Indels_concordant': 'NA',
            'Callable': '0.31%'
        }
    ]
}
