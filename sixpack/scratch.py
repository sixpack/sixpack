import db
from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, NotFound
from werkzeug.utils import redirect
import json
import random

class Sixpack(object):

    def __init__(self):
        self.redis = db.REDIS

        self.url_map = Map([
            Rule('/', endpoint='status'),
            Rule('/experiment', endpoint='start_experiment')
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

    def on_start_experiment(self, request):
        alts = request.args.getlist('alternatives')
        test = request.args.get('experiment')
        force = request.args.get('force', None)
        client_id = request.args.get('client_id')

        seq_id = db.sequential_id('sequential_ids', client_id)

        # Do we have a forced choice?
        # TODO
        if force and force in alts:
            return json_resp(force)

        chosen_alternative = chose_alternative(alts)

        # Does this user have a participation for this test?
        db.record_participation(seq_id, test, alts[0])
            # return that
        # No?! Congradulations
            # Choose an alte, and store it

        resp = {
            'chosen_alt': chosen_alternative,
            'experiment': test,
            'client_id': client_id,
            'seq_id': seq_id
        }
        return json_resp(resp)

# This will change significantly when steve gets a hold of it.
def chose_alternative(alternatives):
    return random.choice(alternatives)

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