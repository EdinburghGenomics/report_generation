__author__ = 'mwham'
import sys
import demultiplexing_report
import requests


transformations = {
    '%': 'pc',
    ' ': '_'
}
deletions = '()'


def sanitise(in_str):
    for k, v in transformations.items():
        in_str = in_str.replace(k, v)
    for char in deletions:
        in_str = in_str.replace(char, '')
    return in_str


def csv_to_dict_list(in_csv):
    header = in_csv[0]
    for line in in_csv[1:]:
        dict_line = {}
        for idx, k in enumerate(header):
            dict_line[sanitise(k)] = line[idx]
        yield dict_line


def insert(payload):
    curl_data = {
        'run_id': '150723_test',
        'lane': 1,
        'barcode': 'TESTTEST',
        'sample_project': '10015AT_test',
        'sample_id': '10015AT0002_test',
        'library_id': 'LP600_test',
        'report_type': 'demultiplexing',
        'payload': payload
    }
    requests.post('http://127.0.0.1:5002/api/0.1/data_points', json=curl_data)


if __name__ == '__main__':
    reports = demultiplexing_report.main(sys.argv[2])

    for report in ('Demultiplexing results', 'Unexpected barcodes results'):
        json_inserts = csv_to_dict_list(reports[report])

        for x in json_inserts:
            insert(x)
