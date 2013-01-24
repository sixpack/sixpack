import db
from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, BadRequest

import json

from models import Experiment, Client


class Sixpack(object):

    def __init__(self, redis_conn):
        self.redis = redis_conn

        self.url_map = Map([
            Rule('/', endpoint='home'),
            Rule('/_status', endpoint='status'),
            Rule('/participate', endpoint='participate'),
            Rule('/convert', endpoint='convert'),
            Rule('/favicon.ico', endpoint='favicon')
        ])

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        response = self.dispatch_request(request)
        return response(environ, start_response)

    def dispatch_request(self, request):
        adapter = self.url_map.bind_to_environ(request.environ)
        try:
            endpoint, values = adapter.match()
            return getattr(self, 'on_' + endpoint)(request, **values)
        except HTTPException, e:
            return e

    # housekeeping endpoints
    def on_status(self, request):
        code, message = 200, 'ok'
        try:
            self.redis.ping()
        except:
            code, message = 503, '[REDIS] is unavailable'

        return json_resp({'status': message, 'code': code}, code)

    def on_home(self, request):
        dales = """
                 ,-"-.__,-"-.__,-"-..
                ( C>  )( C>  )( C>  ))
               /.`-_-'||`-_-'||`-_-'/
              /-"-.--,-"-.--,-"-.--/|
             ( C>  )( C>  )( C>  )/ |
            (|`-_-',.`-_-',.`-_-'/  |
             `-----++-----++----'|  |
             |     ||     ||     |-'
             |     ||     ||     |
             |     ||     ||     |
             `-_-'  `-_-'  `-_-'
        http://github.com/seatgeek/sixpack"""
        return Response(dales)

    def on_favicon(self, request):
        return Response()

    # core endpoints
    def on_convert(self, request):
        experiment_name = request.args.get('experiment')

        client_id = request.args.get('client_id')

        if client_id is None or experiment_name is None:
            raise BadRequest

        client = Client(self.redis, client_id)
        experiment = Experiment.find(experiment_name, self.redis)
        experiment.convert(client.get_sequential_id())

        return json_resp({'status': 'ok'})

    def on_participate(self, request):
        alts = request.args.getlist('alternatives')
        experiment_name = request.args.get('experiment')
        force = request.args.get('force')
        client_id = request.args.get('client_id')

        if client_id is None or experiment_name is None or alts is None:
            raise BadRequest

        # Get the experiment ready for action
        client = Client(self.redis, client_id)
        seq_id = client.get_sequntial_id()
        experiment = Experiment.find_or_create(experiment_name, alts, self.redis)

        if force and force in alts:
            alternative = force
        elif experiment.has_winner():
            alternative = experiment.get_winner().name
        else:
            alternative = experiment.get_alternative(seq_id).name

        resp = {
            'alternative': alternative,
            'experiment': {
                'name': experiment.name,
                'version': experiment.version()
            },
            'client_id': client_id,
            'seq_id': seq_id
        }
        return json_resp(resp)

# troll helper
def json_resp(thing, status=None):
    resp = Response(json.dumps(thing), status=status)
    resp.headers['Context-Type'] = 'application/json'
    return resp

def create_app():
    app = Sixpack(db.REDIS)

    return app

if __name__ == '__main__':
    from werkzeug.serving import run_simple
    app = create_app()
    run_simple('127.0.0.1', 5000, app, use_debugger=True, use_reloader=True)