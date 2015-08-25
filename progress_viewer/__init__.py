__author__ = 'mwham'
import flask as fl
import os
import sys

datasets_path = sys.argv[1]
DEBUG = False

app = fl.Flask(__name__)
app.config.from_object(__name__)


@app.route('/')
def main_page():
    return fl.render_template('main.html')


@app.route('/report')
def report():
    return fl.render_template('report.html', datasets=report_datasets())


def report_datasets():
    reports = []
    for d in _listdirs(datasets_path):
        if _is_complete(d):
            s = 'complete'
        elif _is_active(d):
            s = 'active'
        else:
            s = 'other'
        reports.append((d, s))
    return reports


def _is_complete(dataset):
    return os.path.isfile(os.path.join(datasets_path, '.' + dataset + '.complete'))


def _is_active(dataset):
    return os.path.isfile(os.path.join(datasets_path, '.' + dataset + '.active'))


def _listdirs(path):
    return [x for x in os.listdir(path) if os.path.isdir(os.path.join(datasets_path, x))]


if __name__ == '__main__':
    app.run('localhost', 5000)
