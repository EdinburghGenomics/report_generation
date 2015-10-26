__author__ = 'mwham'
import eve


settings = {
    'DOMAIN': {
        'things': {
            'url': 'things',
            'resource_methods': ['GET', 'POST', 'DELETE'],
            'item_title': 'thing',

            'schema': {

                'run_id': {
                    'type': 'string',
                    'required': True
                },
                'sample_id': {
                    'type': 'string',
                    'required': True
                },
                'sample_project': {
                    'type': 'string',
                    'required': True
                },
                'source': {
                    'type': 'string',
                    'required': True,
                    'allowed': ['bcbio', 'clarity', 'analysis_driver']
                },
                'report_type': {'type': 'string'},  # e.g. variant_calling, demultiplexing, etc.
                'payload': {'type': 'dict'}

            },

            'additional_lookup': {
                'field': 'sample_id',
                'url': 'regex("[\w]+")'
            }
        }
    },
    'MONGO_HOST': 'localhost',
    'MONGO_PORT': 5001,
    'MONGO_DBNAME': 'test_db',

    'RESOURCE_METHODS': ['GET', 'POST', 'DELETE'],
    'ITEM_METHODS': ['GET', 'PUT', 'DELETE']
}

"""
example PUT query:
curl -d '{"run_id": "150723_test", "sample_project": "10015AT", "sample_id": "10015AT0002", "report_type": "test_bcbio_report", "source": "bcbio", "payload": {"alignment": "okay", "variant_calling": "okay", "annotation": "oh noes!"}}' http://127.0.0.1:5000/things -H 'Content-Type: application/json'

querying with Python syntax:
curl -i -g 'http://127.0.0.1:5000/things?where=sample_project=="10015AT"'
http://127.0.0.1:5000/things?where=sample_project==%2210015AT%22

and MongoDB syntax:
curl -i -g 'http://127.0.0.1:5000/things?where={"sample_project":"10015AT"}'
http://127.0.0.1:5000/things?where={%22sample_project%22:%2210015AT%22}
"""

app = eve.Eve(settings=settings)


if __name__ == '__main__':
    app.run()
