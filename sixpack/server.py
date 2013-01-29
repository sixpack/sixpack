import re
from urllib import unquote
from socket import inet_aton
import json
import functools

import db
from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException
import redis

from models import Experiment, Client
from config import CONFIG as cfg


def service_unavailable_on_connection_error(fn):
    @functools.wraps(fn)
    def impl(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except redis.ConnectionError:
            return json_resp({"message":"Service Unavailable"}, 503)
    return impl


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

    @service_unavailable_on_connection_error
    def on_status(self, request):
        self.redis.ping()
        return json_resp({"message": "ok"})

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

    @service_unavailable_on_connection_error
    def on_convert(self, request):
        experiment_name = request.args.get('experiment')

        client_id = request.args.get('client_id')

        if client_id is None or experiment_name is None:
            return json_resp({'status': 'missing arguments'}, 400)

        if should_exclude_visitor(request):
            return json_resp({'status': 'ok'})

        client = Client(client_id, self.redis)
        experiment = Experiment.find(experiment_name, self.redis)
        experiment.convert(client)

        return json_resp({'status': 'ok'})

    @service_unavailable_on_connection_error
    def on_participate(self, request):
        alts = request.args.getlist('alternatives')
        experiment_name = request.args.get('experiment')
        force = request.args.get('force')
        client_id = request.args.get('client_id')

        if client_id is None or experiment_name is None or alts is None:
            return json_resp({'status': 'missing arguments'}, 400)

        if should_exclude_visitor(request):
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

def should_exclude_visitor(request):
    user_agent = request.args.get('user_agent')
    ip_address = request.args.get('ip_address')

    return is_robot(user_agent) or is_ignored_ip(ip_address)

def is_robot(user_agent):
    try:
        regex = re.compile(r"{0}".format(cfg.get('robot_regex')), re.I)
        return regex.match(unquote(user_agent))
    except:
        return False # TODO Not sure if default should be true or false

def is_ignored_ip(ip_address):
    # Ignore invalid/local IP addresses
    try:
        inet_aton(unquote(ip_address))
    except:
        return False # TODO Same as above not sure of default

    return unquote(ip_address) in cfg.get('ignored_ip_addresses')

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