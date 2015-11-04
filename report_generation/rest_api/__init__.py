__author__ = 'mwham'
import eve


settings = {
    'DOMAIN': {

        'run_elements': {  # for demultiplexing reports, etc
            'url': 'run_elements',
            'resource_methods': ['GET', 'POST', 'DELETE'],
            'item_title': 'element',

            'schema': {

                'run_id': {'type': 'string', 'required': True},
                'lane': {
                   'type': 'number',
                   'required': True
                },
                'barcode': {
                    'type': 'string',
                    'required': True
                },
                'sample_id': {
                    'type': 'string',
                    'required': True  # for now, treat sample_id and library_id as 1:1 equivalent
                },
                'library_id': {
                    'type': 'string',
                    'required': True
                },
                'sample_project': {
                    'type': 'string',
                    'required': True
                },
                'pc_pass_filter': {
                    'type': 'number',
                    'required': True
                },
                'passing_filter_reads': {
                    'type': 'string',
                    'required': True
                },
                'yield_in_Gb': {
                    'type': 'string',
                    'required': True
                },
                'pc_q30_R1': {
                    'type': 'string',
                    'required': True
                },
                'pc_q30_R2': {
                    'type': 'string',
                    'required': True
                }

            }

        },

        'samples': {
            'url': 'samples',

            'schema': {

                'project': {'type': 'string', 'required': True},
                'sample_id': {'type': 'string', 'required': True},
                'library_id': {'type': 'string', 'required': True},
                'user_sample_id': {'type': 'string', 'required': True},
                'yield_in_Gb': {'type': 'string', 'required': True},
                'pc_q30_R1': {'type': 'string', 'required': True},
                'pc_q30_R2': {'type': 'string', 'required': True},
                'initial_reads': {'type': 'string', 'required': True},  # used to be 'no adaptor reads'
                'passing_filter_reads': {'type': 'string', 'required': True},
                'nb_mapped_reads': {'type': 'string', 'required': True},
                'pc_mapped_reads': {'type': 'string', 'required': True},
                'nb_properly_mapped_reads': {'type': 'string', 'required': True},
                'pc_properly_mapped_reads': {'type': 'string', 'required': True},
                'nb_duplicate_reads': {'type': 'string', 'required': True},
                'pc_duplicate_reads': {'type': 'string', 'required': True},
                'median_coverage': {'type': 'string', 'required': True},
                'pc_callable': {'type': 'string', 'required': True}

            }
        },

        # 'lanes': {
        #     'schema': {
        #         'run_id': {
        #             'type': 'string',
        #             'required': True
        #         },
        #         'lane_number': {
        #
        #         },
        #
        #         'pc_pass_filter': {
        #             'type': 'number',
        #
        #         }
        #     }
        # }

        'unexpected_barcodes': {
            'url': 'unexpected_barcodes',

            'schema': {

                'run_id': {'type': 'string'},
                'lane': {'type': 'string'},
                'barcode': {'type': 'string'},
                'passing_filter_reads': {'type': 'string'},
                'pc_reads_in_lane': {'type': 'string'}
            }
        }

    },

    'MONGO_HOST': 'localhost',
    'MONGO_PORT': 5001,
    'MONGO_DBNAME': 'test_db',
    'ITEMS': 'data',

    'JSONP_ARGUMENT': 'callback',
    'URL_PREFIX': 'api',
    'API_VERSION': '0.1',

    'RESOURCE_METHODS': ['GET', 'DELETE'],
    'ITEM_METHODS': ['GET', 'PUT', 'DELETE']
}


app = eve.Eve(settings=settings)

"""
example PUT query:
curl -d '{"run_id": "150723_test", "sample_project": "10015AT", "sample_id": "10015AT0002", "report_type": "test_bcbio_report", "source": "bcbio", "payload": {"alignment": "okay", "variant_calling": "okay", "annotation": "oh noes!"}}' http://127.0.0.1:5000/things -H 'Content-Type: application/json'
curl -d '{"run_id": "150723_test", "lane": 1, "barcode": "TESTTEST", "sample_project": "10015AT_test", "sample_id": "10015AT0002_test", "library_id": "LP600_test", "payload": {"Yield_Gb": "0.09", "pcPF": "75.04%", "Barcode": "GAGATTCC", "pc_of_Read": "12.76%", "pcQ30_R1": "72.57%", "Project": "10015AT", "Lane": "1", "Library": "LP6002014-DTP_A04", "Nb_of_Read": "619778"}}' http://127.0.0.1:5002/data_points -H 'Content-Type: application/json'

querying with Python syntax:
curl -i -g 'http://127.0.0.1:5000/things?where=sample_project=="10015AT"'
http://127.0.0.1:5000/things?where=sample_project==%2210015AT%22

and MongoDB syntax:
curl -i -g 'http://127.0.0.1:5000/things?where={"sample_project":"10015AT"}'
http://127.0.0.1:5000/things?where={%22sample_project%22:%2210015AT%22}
"""

if __name__ == '__main__':
    app.run(port=5002, debug=True)
