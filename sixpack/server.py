import re
from socket import inet_aton
import sys
from urllib import unquote

import dateutil.parser
from redis import ConnectionError
from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, NotFound

from . import __version__
from api import participate, convert

from config import CONFIG as cfg
from utils import to_bool

try:
    import db
except ConnectionError:
    print "Redis is currently unavailable or misconfigured"
    sys.exit()

from models import Experiment, Client
from utils import service_unavailable_on_connection_error, json_error, json_success


class Sixpack(object):

    def __init__(self, redis_conn):
        self.redis = redis_conn

        self.config = cfg

        self.url_map = Map([
            Rule('/', endpoint='home'),
            Rule('/_status', endpoint='status'),
            Rule('/participate', endpoint='participate'),
            Rule('/convert', endpoint='convert'),
            Rule('/experiments/<name>', endpoint='experiment_details'),
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
        kpi = request.args.get('kpi', None)

        if client_id is None or experiment_name is None:
            return json_error({'message': 'missing arguments'}, request, 400)

        dt = None
        if request.args.get("datetime"):
            dt = dateutil.parser.parse(request.args.get("datetime"))

        try:
            alt = convert(experiment_name, client_id, kpi=kpi, datetime=dt, redis=self.redis)
        except ValueError as e:
            return json_error({'message': str(e)}, request, 400)

        resp = {
            'alternative': {
                'name': alt.name
            },
            'experiment': {
                'name': alt.experiment.name,
            },
            'conversion': {
                'value': None,
                'kpi': kpi
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
        traffic_fraction = request.args.get('traffic_fraction')
        if traffic_fraction is not None:
            traffic_fraction = float(traffic_fraction)
        prefetch = to_bool(request.args.get('prefetch', 'false'))

        if client_id is None or experiment_name is None or alts is None:
            return json_error({'message': 'missing arguments'}, request, 400)

        dt = None
        if request.args.get("datetime"):
            dt = dateutil.parser.parse(request.args.get("datetime"))

        if should_exclude_visitor(request):
            exp = Experiment.find(experiment_name, redis=self.redis)
            if exp.winner is not None:
                alt = exp.winner
            else:
                alt = exp.control
        else:
            try:
                alt = participate(experiment_name, alts, client_id,
                                  force=force, traffic_fraction=traffic_fraction,
                                  prefetch=prefetch, datetime=dt, redis=self.redis)
            except ValueError as e:
                return json_error({'message': str(e)}, request, 400)

        resp = {
            'alternative': {
                'name': alt.name
            },
            'experiment': {
                'name': alt.experiment.name,
            },
            'client_id': client_id,
            'status': 'ok'
        }

        return json_success(resp, request)

    @service_unavailable_on_connection_error
    def on_experiment_details(self, request, name):
        exp = Experiment.find(name, redis=self.redis)
        if exp is None:
            return json_error({'message': 'experiment not found'}, request, 404)

        return json_success(exp.objectify_by_period('day', True), request)


def should_exclude_visitor(request):
    user_agent = request.args.get('user_agent')
    ip_address = request.args.get('ip_address')

    return is_robot(user_agent) or is_ignored_ip(ip_address)


def is_robot(user_agent):
    if user_agent is None:
        return False
    regex = re.compile(r"{0}".format(cfg.get('robot_regex')), re.I)
    return regex.search(unquote(user_agent)) is not None


def is_ignored_ip(ip_address):
    # Ignore invalid/local IP addresses
    try:
        inet_aton(unquote(ip_address))
    except:
        return False  # TODO Same as above not sure of default

    return unquote(ip_address) in cfg.get('ignored_ip_addresses')


# Method to run with built-in server
def create_app():
    app = Sixpack(db.REDIS)
    return app


# Method to run with gunicorn
def start(environ, start_response):
    app = Sixpack(db.REDIS)
    return app(environ, start_response)
