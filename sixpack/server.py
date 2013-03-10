import json
import re
from socket import inet_aton
from urllib import unquote

import redis
from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, NotFound
import dateutil.parser

from . import __version__
import decorator
from config import CONFIG as cfg
import db
from models import Experiment, Client


@decorator.decorator
def service_unavailable_on_connection_error(f, *args, **kwargs):
    try:
        return f(*args, **kwargs)
    except redis.ConnectionError:
        return json_error({"message": "service unavilable"}, None, 503)


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
        except NotFound:
            return json_error({"message": "not found"}, request, 404)
        except HTTPException:
            return json_error({"message": "an internal error has occurred"}, request, 500)

    @service_unavailable_on_connection_error
    def on_status(self, request):
        self.redis.ping()
        return json_success({'version': __version__}, request)

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
        if should_exclude_visitor(request):
            return json_success({'excluded': 'true'}, request)

        experiment_name = request.args.get('experiment')

        client_id = request.args.get('client_id')

        if client_id is None or experiment_name is None:
            return json_error({'message': 'missing arguments'}, request, 400)

        client = Client(client_id, self.redis)

        try:
            experiment = Experiment.find(experiment_name, self.redis)
            if cfg.get('enabled', True):
                dt = None
                if request.args.get("datetime"):
                    dt = dateutil.parser.parse(request.args.get("datetime"))
                alternative = experiment.convert(client, dt=dt)
            else:
                alternative = experiment.control().name
        except ValueError as e:
            return json_error({'message': str(e)}, request, 400)

        resp = {
            'alternative': {
                'name': alternative
            },
            'experiment': {
                'name': experiment.name,
                'version': experiment.version()
            },
            'conversion': {
                'value': None
            },
            'client_id': client_id
        }

        return json_success(resp, request)

    @service_unavailable_on_connection_error
    def on_participate(self, request):
        alts = request.args.getlist('alternatives')
        experiment_name = request.args.get('experiment')
        force = request.args.get('force')
        client_id = request.args.get('client_id')

        if client_id is None or experiment_name is None or alts is None:
            return json_error({'message': 'missing arguments'}, request, 400)

        # Get the experiment ready for action
        client = Client(client_id, self.redis)
        experiment = Experiment.find_or_create(experiment_name, alts, self.redis)

        resp = {}

        if force and force in alts:
            alternative = force
        elif not cfg.get('enabled', True) or should_exclude_visitor(request):
            alternative = alts[0]
            resp['excluded'] = True
        elif experiment.has_winner():
            alternative = experiment.get_winner().name
        else:
            dt = None
            if request.args.get("datetime"):
                dt = dateutil.parser.parse(request.args.get("datetime"))
            alternative = experiment.get_alternative(client, dt=dt).name

        resp = {
            'alternative': {
                'name': alternative
            },
            'experiment': {
                'name': experiment.name,
                'version': experiment.version()
            },
            'client_id': client_id,
            'status': 'ok'
        }

        return json_success(resp, request)


def should_exclude_visitor(request):
    user_agent = request.args.get('user_agent')
    ip_address = request.args.get('ip_address')

    return is_robot(user_agent) or is_ignored_ip(ip_address)


def is_robot(user_agent):
    try:
        regex = re.compile(r"{0}".format(cfg.get('robot_regex')), re.I)
        return regex.match(unquote(user_agent))
    except:
        return False  # TODO Not sure if default should be true or false


def is_ignored_ip(ip_address):
    # Ignore invalid/local IP addresses
    try:
        inet_aton(unquote(ip_address))
    except:
        return False  # TODO Same as above not sure of default

    return unquote(ip_address) in cfg.get('ignored_ip_addresses')


def json_error(resp, request, status=None):
    default = {'status': 'failed'}
    resp = dict(default.items() + resp.items())

    return _json_resp(resp, request, status)


def json_success(resp, request):
    default = {'status': 'ok'}
    resp = dict(default.items() + resp.items())

    return _json_resp(resp, request, 200)  # Always a 200 when success is called


def _json_resp(in_dict, request, status=None):
    headers = {'Content-Type': 'application/json'}
    data = json.dumps(in_dict)
    callback = request and request.args.get('callback')
    if callback and re.match("^\w[\w'\-\.]*$", callback):
        headers["Content-Type"] = "application/javascript"
        data = "%s(%s)" % (callback, data)

    return Response(data, status=status, headers=headers)


# Method to run with built-in server
def create_app():
    app = Sixpack(db.REDIS)

    return app


# Method to run with gunicorn
def start(environ, start_response):
    app = Sixpack(db.REDIS)

    return app(environ, start_response)
