import db
from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, NotFound
from werkzeug.utils import redirect
import json

from models import Experiment
#from models.alternative import Alternative

class Sixpack(object):

    def __init__(self):
        self.redis = db.REDIS

        self.url_map = Map([
            Rule('/', endpoint='status'),
            Rule('/experiment', endpoint='start_experiment'),
            Rule('/convert', endpoint='convert')
        ])

    def dispatch_request(self, request):
        adapter = self.url_map.bind_to_environ(request.environ)
        try:
            endpoint, values = adapter.match()
            return getattr(self, 'on_' + endpoint)(request, **values)
        except HTTPException, e:
            return e

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        response = self.dispatch_request(request)
        return response(environ, start_response)

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)

    # Routes are below, investigate moving these out of this file
    def on_status(self, request):
        status = {
            'status': 'ok'
        }
        return json_resp(status)

    def on_convert(self, request):
        experiment_name = request.args.get('experiment')

        client_id = request.args.get('client_id')
        seq_id = db.sequential_id('sequential_ids', client_id)

        experiment = Experiment.find(experiment_name)
        experiment.convert(seq_id)

        # did client convert already?

        if client_id is None or experiment_name is None:
            raise Exception('You forgot something, bro')

        return json_resp({'status': 'ok'})

    def on_start_experiment(self, request):
        alts = request.args.getlist('alternatives')
        experiment_name = request.args.get('experiment')
        force = request.args.get('force', None)
        client_id = request.args.get('client_id')

        if client_id is None or experiment_name is None or alts is None:
            raise Exception('You forgot something, bro')

        if force and force in alts:
            return json_resp(force)

        # This should be wrapped up and moved out of the 'controller'
        seq_id = db.sequential_id('sequential_ids', client_id)
        experiment = Experiment.find_or_create(experiment_name, alts)
        alternative = experiment.get_alternative(seq_id)

        # Did we pick a winner?
        #  return it
        # otherwise
        #  clean old versions
        #  exclusions
        #  get user? # this is based on client now.

        resp = {
            'chosen_alt': alternative,
            'experiment': experiment_name,
            'client_id': client_id,
            'seq_id': seq_id
        }
        return json_resp(resp)

# troll helper
def json_resp(thign):
    resp = Response(json.dumps(thign))
    resp.headers['Context-Type'] = 'application/json'
    return resp

def create_app():
    app = Sixpack()

    return app

if __name__ == '__main__':
    from werkzeug.serving import run_simple
    app = create_app()
    run_simple('127.0.0.1', 5000, app, use_debugger=True, use_reloader=True)