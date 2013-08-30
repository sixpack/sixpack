from flask import Flask
from flask import render_template, abort, request, url_for, redirect, jsonify, make_response
from flask.ext.seasurf import SeaSurf
from flask.ext.assets import Environment, Bundle
from flask_debugtoolbar import DebugToolbarExtension
from markdown import markdown

from . import __version__
from config import CONFIG as cfg
import db
from models import Experiment
import utils

app = Flask(__name__)
csrf = SeaSurf(app)

js = Bundle('js/vendor/jquery.js', 'js/vendor/d3.js',
            'js/vendor/bootstrap.js', 'js/experiment.js', 'js/chart.js',
            'js/sixpack.js', 'js/vendor/underscore-min.js', 'js/vendor/spin.min.js',
            'js/vendor/waypoints.min.js', 'js/vendor/zeroclipboard.min.js',
            filters=['closure_js'],
            output="{0}/sixpack.js".format(cfg.get('asset_path', 'gen')))

css = Bundle('css/vendor/bootstrap.css',
             'css/vendor/bootstrap-responsive.css', 'css/sixpack.css',
             filters=['yui_css'],
             output="{0}/sixpack.css".format(cfg.get('asset_path', 'gen')))

assets = Environment(app)
assets.register('js_all', js)
assets.register('css_all', css)


@app.route('/_status')
@utils.service_unavailable_on_connection_error
def status():
    db.REDIS.ping()
    return utils.json_success({'version': __version__}, request)


@app.route("/")
def hello():
    experiments = Experiment.all(db.REDIS)
    experiments = [exp.name for exp in experiments]
    return render_template('dashboard.html', experiments=experiments, page='home')


@app.route('/archived')
def archived():
    experiments = Experiment.all(db.REDIS, False)
    experiments = [exp.name for exp in experiments if exp.is_archived()]
    return render_template('dashboard.html', experiments=experiments, page='archived')


@app.route('/experiments.json')
def experiment_list():
    experiments = Experiment.all(db.REDIS)
    period = determine_period()
    experiments = [simple_markdown(exp.objectify_by_period(period)) for exp in experiments]
    return jsonify({'experiments': experiments})


# Details for experiment
@app.route("/experiments/<experiment_name>/")
def details(experiment_name):
    experiment = find_or_404(experiment_name)
    return render_template('details.html', experiment=experiment)


@app.route("/experiments/<experiment_name>.json")
def json_details(experiment_name):
    experiment = find_or_404(experiment_name)
    period = determine_period()
    obj = simple_markdown(experiment.objectify_by_period(period))
    return jsonify(obj)


@app.route("/experiments/<experiment_name>/export", methods=['POST'])
def export(experiment_name):
    experiment = find_or_404(experiment_name)

    response = make_response(experiment.csvify())
    response.headers["Content-Type"] = "text/csv"
    # force a download with the content-disposition headers
    filename = "sixpack_export_{0}".format(experiment_name)
    response.headers["Content-Disposition"] = "attachment; filename={0}.csv".format(filename)

    return response


# Set winner for an experiment
@app.route("/experiments/<experiment_name>/winner/", methods=['POST'])
def set_winner(experiment_name):
    experiment = find_or_404(experiment_name)
    experiment.set_winner(request.form['alternative_name'])

    return redirect(url_for('details', experiment_name=experiment.name))


# Reset experiment
@app.route("/experiments/<experiment_name>/reset/", methods=['POST'])
def reset_experiment(experiment_name):
    experiment = find_or_404(experiment_name)
    experiment.reset()

    return redirect(url_for('details', experiment_name=experiment.name))


# Reset experiment winner
@app.route("/experiments/<experiment_name>/winner/reset/", methods=['POST'])
def reset_winner(experiment_name):
    experiment = find_or_404(experiment_name)
    experiment.reset_winner()

    return redirect(url_for('details', experiment_name=experiment.name))


# Delete experiment
@app.route("/experiments/<experiment_name>/delete/", methods=['POST'])
def delete_experiment(experiment_name):
    experiment = find_or_404(experiment_name)
    experiment.delete()

    return redirect(url_for('hello'))


# Archive experiment
@app.route("/experiments/<experiment_name>/archive", methods=['POST'])
def toggle_experiment_archive(experiment_name):
    experiment = find_or_404(experiment_name)
    if experiment.is_archived():
        experiment.unarchive()
    else:
        experiment.archive()

    return redirect(url_for('details', experiment_name=experiment.name))


@app.route("/experiments/<experiment_name>/description", methods=['POST'])
def update_experiment_description(experiment_name):
    experiment = find_or_404(experiment_name)

    experiment.update_description(request.form['description'])

    return redirect(url_for('details', experiment_name=experiment.name))


@app.route('/favicon.ico')
def favicon():
    return ''


@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500


def find_or_404(experiment_name):
    try:
        exp = Experiment.find(experiment_name, db.REDIS)
        if request.args.get('kpi'):
            exp.set_kpi(request.args.get('kpi'))
        return exp
    except ValueError:
        abort(404)


def determine_period():
    period = request.args.get('period', 'day')
    if period not in ['day', 'week', 'month', 'year']:
        err = {'error': 'invalid argument: {0}'.format(period), 'status': 400}
        abort(400, jsonify(err))
    return period


def simple_markdown(experiment):
    description = experiment['description']
    if description and description != '':
        experiment['pretty_description'] = markdown(description)
    return experiment


app.secret_key = cfg.get('secret_key')
app.jinja_env.filters['number_to_percent'] = utils.number_to_percent
app.jinja_env.filters['number_format'] = utils.number_format
toolbar = DebugToolbarExtension(app)


def start(environ, start_response):
    return app(environ, start_response)
