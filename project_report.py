#!/usr/bin/env python
from argparse import ArgumentParser
import csv
from cStringIO import StringIO
from genologics.lims import Lims
import re
import logging
import sys
import os
from xhtml2pdf import pisa
from jinja2 import Environment, FileSystemLoader
from report_generation.config import Configuration
import yaml

__author__ = 'tcezard'


app_logger = logging.getLogger(__name__)

def get_pdf(html_string):
    pdf = StringIO()
    html_string = html_string.encode('utf-8')
    pisa.CreatePDF(StringIO(html_string), pdf)
    return pdf

cfg = Configuration()

def getFolderSize(folder):
    total_size = os.path.getsize(folder)
    for item in os.listdir(folder):
        itempath = os.path.join(folder, item)
        if os.path.isfile(itempath):
            total_size += os.path.getsize(itempath)
        elif os.path.isdir(itempath):
            total_size += getFolderSize(itempath)
    return total_size

class ProjectReport:

    def __init__(self, project_name, project_path):
        self.project_name = project_name
        self.project_path = project_path
        self.lims=Lims(**cfg.get('clarity'))
        self.params = {'project_name':project_name}
        self.results = {}
        self.fill_sample_names_from_lims()
        self.samples_delivered = self.read_metrics_csv(os.path.join(self.project_path, 'metrics_summary.csv'))
        self.get_sample_param()


    def fill_sample_names_from_lims(self):
        samples = self.lims.get_samples(projectname=self.project_name)
        self.samples = [s.name for s in samples]
        self.modified_samples = [re.sub(r'[: ]','_', s.name) for s in samples]

    def get_library_workflow_from_sample(self, sample_name):
        samples = self.lims.get_samples(projectname=self.project_name, name=sample_name)
        if len(samples) == 1:
            return samples[0].udf.get('Prep Workflow')
        else:
            app_logger.error('%s samples found for sample name %s'%sample_name)

    def parse_program_csv(self, program_csv):
        all_programs = {}
        with open(program_csv) as open_prog:
            for row in csv.reader(open_prog):
                all_programs[row[0]]=row[1]
        for p in ['bcbio', 'bwa', 'gatk', 'samblaster']:
            self.params[p + '_version']=all_programs.get(p)

    def parse_project_summary_yaml(self, summary_yaml):
        with open(summary_yaml, 'r') as open_file:
            full_yaml = yaml.safe_load(open_file)
        sample_yaml=full_yaml['samples'][0]
        self.params['bcbio_version'] = os.path.basename(os.path.dirname(sample_yaml['dirs']['galaxy'])).split('-')[1]
        if sample_yaml['genome_build'] == 'hg38':
            self.params['genome_version'] = 'GRCh38'

    def read_metrics_csv(self, metrics_csv):
        samples_to_info={}
        with open(metrics_csv) as open_metrics:
            reader = csv.DictReader(open_metrics, delimiter='\t', quoting=csv.QUOTE_NONE)
            for row in reader:
                samples_to_info[row['Sample Id']] = row
        return samples_to_info

    def get_sample_param(self):
        self.fill_sample_names_from_lims()
        project_size = 0
        library_workflows=set()
        for sample in self.samples:
            library_workflow = self.get_library_workflow_from_sample(sample)
            library_workflows.add(library_workflow)
        if len(library_workflows) == 1 :
            self.library_workflow = library_workflows.pop()
        else:
            app_logger.error('More than one workfkow used in project %s'%self.project_name)

        if self.library_workflow in ['TruSeq Nano DNA Sample Prep', None] :
            self.template = 'truseq_nano_template.html'
            self.params['adapter1'] = "AGATCGGAAGAGCACACGTCTGAACTCCAGTCA"
            self.params['adapter2'] = "AGATCGGAAGAGCGTCGTGTAGGGAAAGAGTGT"
        else:
            app_logger.error('Unknown library workflow %s for project %s'%(self.library_workflow, self.project_name))
        for sample in set(self.modified_samples):
            sample_folder=os.path.join(self.project_path, sample)
            if os.path.exists(sample_folder):
                size = getFolderSize(sample_folder)
                project_size += size
                program_csv = os.path.join(sample_folder, 'programs.txt')
                if not os.path.exists(program_csv):
                    program_csv = os.path.join(sample_folder, '.qc', 'programs.txt')
                self.parse_program_csv(program_csv)
                summary_yaml = os.path.join(sample_folder, 'project-summary.yaml')
                if not os.path.exists(summary_yaml):
                    summary_yaml = os.path.join(sample_folder, '.qc', 'project-summary.yaml')
                self.parse_project_summary_yaml(summary_yaml)

        self.results['project_name']=['Project name:',self.project_name]
        self.results['project_size']=['Total folder size:','%.2fTb'%(project_size/1000000000000.0)]
        self.results['nb_sample']=['Number of sample:', len(self.samples)]
        self.results['nb_sample_delivered']=['Number of sample delivered:',len(self.samples_delivered)]
        yields = [float(self.samples_delivered[s]['Yield']) for s in self.samples_delivered]
        self.results['yield']=['Total yield Gb:','%.2f'%sum(yields)]
        self.results['mean_yield']=['Average yield Gb:','%.1f'%(sum(yields)/max(len(yields), 1))]
        coverage = [float(self.samples_delivered[s]['Mean coverage']) for s in self.samples_delivered]
        self.results['coverage']=['Average coverage per samples:','%.2f'%(sum(coverage)/max(len(coverage), 1))]
        self.results_order=['project_name','nb_sample','nb_sample_delivered', 'yield', 'mean_yield', 'coverage', 'project_size']


    def generate_report(self):
        env = Environment(loader=FileSystemLoader('templates'))
        template = env.get_template(self.template)
        output = template.render(results_order=self.results_order, results=self.results, **self.params)
        pdf = get_pdf(output)
        with open('project_%s_report.pdf'%self.project_name, 'w') as open_pdf:
            open_pdf.write(pdf.getvalue())

    def __str__(self):
        pass




def main():
    #Setup options
    argparser=_prepare_argparser()
    args = argparser.parse_args()
    logging.StreamHandler()
    handler = logging.StreamHandler(stream=sys.stdout, )
    handler.setLevel(logging.DEBUG)
    logging.getLogger('xhtml2pdf').addHandler(handler)
    app_logger.addHandler(handler)
    ProjectReport(args.project_name, args.project_path).generate_report()

def _prepare_argparser():
    """Prepare optparser object. New arguments will be added in this
    function first.
    """
    description = """Simple script that parse bcbio outputs and generate a wiki table"""

    argparser = ArgumentParser(description=description)
    argparser.add_argument("-p", "--project_name", dest="project_name", type=str,
                           help="The name of the project for which a report should be generated.")
    argparser.add_argument("-P", "--project_path", dest="project_path", type=str,
                           help="The path to the project drectory.")


    return argparser


if __name__=="__main__":
    main()