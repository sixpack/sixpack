from flask import Flask
from flask import render_template, abort, request, url_for, redirect, jsonify
from flask.ext.seasurf import SeaSurf
from flask.ext.assets import Environment, Bundle

from config import CONFIG as cfg
from db import REDIS
from models import Experiment
import utils

app = Flask(__name__)
csrf = SeaSurf(app)

js = Bundle('js/jquery.js', 'js/d3.js',
            'js/bootstrap.js', 'js/experiment.js', 'js/chart.js',
            'js/script.js', 'js/underscore-min.js',
            'js/waypoints.min.js',
            filters=['closure_js'],
            output="{0}/sixpack.js".format(cfg.get('asset_path', 'gen')))

css = Bundle('css/bootstrap.css',
             'css/bootstrap-responsive.css', 'css/style.css',
             filters=['yui_css'],
             output="{0}/sixpack.css".format(cfg.get('asset_path', 'gen')))

assets = Environment(app)
assets.register('js_all', js)
assets.register('css_all', css)


# List of experiments
@app.route("/")
def hello():
    #archived = bool(request.args.get('include_archived', False))
    #exclude_archived = not archived
    # TODO: these need to be sorted
    experiments = Experiment.all_names(REDIS)
    return render_template('dashboard.html', experiments=experiments)


# Details for experiment
@app.route("/experiment/<experiment_name>/")
def details(experiment_name):
    experiment = find_or_404(experiment_name)
    return render_template('details.html', experiment=experiment)


@app.route("/experiment/<experiment_name>.json")
def json_details(experiment_name):

    period = request.args.get('period', None)
    if period not in ['day', 'week', 'month', 'year']:
        err = {'error': 'invalid argument: {0}'.format(period), 'status': 400}
        return jsonify(err)

    experiment = find_or_404(experiment_name)
    obj = experiment.objectify_by_period(period)
    return jsonify(obj)


# Set winner for an experiment
@app.route("/experiment/<experiment_name>/winner/", methods=['POST'])
def set_winner(experiment_name):
    experiment = find_or_404(experiment_name)
    experiment.set_winner(request.form['alternative_name'])

    return redirect(url_for('details', experiment_name=experiment.name))


# Reset experiment
@app.route("/experiment/<experiment_name>/reset/", methods=['POST'])
def reset_experiment(experiment_name):
    experiment = find_or_404(experiment_name)
    experiment.reset()

    return redirect(url_for('details', experiment_name=experiment.name))


# Reset experiment winner
@app.route("/experiment/<experiment_name>/winner/reset/", methods=['POST'])
def reset_winner(experiment_name):
    experiment = find_or_404(experiment_name)
    experiment.reset_winner()

    return redirect(url_for('details', experiment_name=experiment.name))


# Delete experiment
@app.route("/experiment/<experiment_name>/delete/", methods=['POST'])
def delete_experiment(experiment_name):
    experiment = find_or_404(experiment_name)
    experiment.delete()

    return redirect(url_for('hello'))


# Archive experiment
@app.route("/experiment/<experiment_name>/archive", methods=['POST'])
def toggle_experiment_archive(experiment_name):
    experiment = find_or_404(experiment_name)
    if experiment.is_archived():
        experiment.unarchive()
    else:
        experiment.archive()

    return redirect(url_for('details', experiment_name=experiment.name))


@app.route("/experiment/<experiment_name>/description", methods=['POST'])
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
        return Experiment.find(experiment_name, REDIS,
                               request.args.get('version', None))
    except:
        abort(404)

app.secret_key = cfg.get('secret_key')
app.jinja_env.filters['number_to_percent'] = utils.number_to_percent
app.jinja_env.filters['number_format'] = utils.number_format


def start(environ, start_response):
    return app(environ, start_response)
