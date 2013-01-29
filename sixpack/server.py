import db
from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException

import json

from models import Experiment, Client
from config import CONFIG as cfg

class Sixpack(object):

    def __init__(self, redis_conn):
        self.redis = redis_conn

        self.config = cfg

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
        https://github.com/seatgeek/sixpack"""
        return Response(dales)

    def on_favicon(self, request):
        return Response()

    # core endpoints
    def on_convert(self, request):
        experiment_name = request.args.get('experiment')

        client_id = request.args.get('client_id')

        if client_id is None or experiment_name is None:
            return json_resp({'status': 'missing arguments'}, 400)

        if self.should_exclude_visitor(request):
            return json_resp({'status': 'ok'})

        # Return control on db failure by default
        if self.config.get('control_on_db_failure'):
            try:
                self.redis.ping()
            except:
                return json_resp({'status': 'ok'}) # not ok?

        client = Client(client_id, self.redis)
        experiment = Experiment.find(experiment_name, self.redis)
        experiment.convert(client)

        if self.config.get('full_response', True):
            resp = {
                'client_id': client_id,
                'status': 'ok'
            }
        else:
            resp = {'s': 'ok'}

        return json_resp(resp)

    def on_participate(self, request):

        alts = request.args.getlist('alternatives')
        experiment_name = request.args.get('experiment')
        force = request.args.get('force')
        client_id = request.args.get('client_id')

        if client_id is None or experiment_name is None or alts is None:
            return json_resp({'status': 'missing arguments'}, 400)

        if self.should_exclude_visitor(request):
            return json_resp({'alternative': alts[0]})

        # Return control on db failure by default
        if self.config.get('control_on_db_failure'):
            try:
                self.redis.ping()
            except:
                return json_resp({'alternative': alts[0]})

        # Get the experiment ready for action
        client = Client(client_id, self.redis)
        experiment = Experiment.find_or_create(experiment_name, alts, self.redis)

        if force and force in alts:
            alternative = force
        elif experiment.has_winner():
            alternative = experiment.get_winner().name
        else:
            alternative = experiment.get_alternative(client).name

        resp = {
            'alternative': alternative,
            'experiment': {
                'name': experiment.name,
                'version': experiment.version()
            },
            'client_id': client_id
        }

        return json_resp(resp)

    def should_exclude_visitor(self, request):
        user_agent = request.args.get('user_agent')
        ip_address = request.args.get('ip_address')

        return self.is_robot(user_agent) or self.is_ignored_ip(ip_address)

    def is_robot(self, user_agent):
        try:
            regex = re.compile(r"{0}".format(self.config.get('robot_regex')), re.I)
            return regex.match(unquote(user_agent))
        except:
            return False

    def is_ignored_ip(self, ip_address):
        return ip_address in self.config.get('ignored_ip_addresses')

def json_resp(in_dict, status=None):
    headers = {'Context-Type': 'application/json'}
    return Response(json.dumps(in_dict), status=status, headers=headers)



# Move these to bin/sixpack
def create_app():
    app = Sixpack(db.REDIS)

    return app

def start(environ, start_response):
    app = Sixpack(db.REDIS)

    return app(environ, start_response)

if __name__ == '__main__':
    from werkzeug.serving import run_simple
    app = create_app()
    run_simple('127.0.0.1', 5000, app, use_debugger=True, use_reloader=True)