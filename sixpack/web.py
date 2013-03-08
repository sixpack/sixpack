from flask import Flask, render_template, abort, request, url_for, redirect
from flask.ext.seasurf import SeaSurf
from flask.ext.assets import Environment, Bundle

from config import CONFIG as cfg
from db import REDIS
from models import Experiment
import utils

app = Flask(__name__)
app.debug = True
csrf = SeaSurf(app)
js = Bundle('js/jquery.js', 'js/d3.js', 'js/bootstrap.js', 'js/bootstrap.min.js', 'js/chart.js', 'js/script.js', 'js/underscore-min.js',
            output='gen/sixpack.js')

css = Bundle('css/bootstrap.css', 'css/bootstrap-responsive.css', 'css/style.css',
             output='gen/sixpack.css')

assets = Environment(app)
assets.register('js_all', js)
assets.register('css_all', css)


# List of experiments
@app.route("/")
def hello():
    archived = bool(request.args.get('include_archived', False))
    exclude_archived = not archived
    experiments = Experiment.all(REDIS, exclude_archived)

    return render_template('dashboard.html', experiments=experiments, include_archived=archived)


# Details for experiment
@app.route("/experiment/<experiment_name>/")
def details(experiment_name):
    experiment = find_or_404(experiment_name)
    return render_template('details.html', experiment=experiment)


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


def find_or_404(experiment_name):
    try:
        return Experiment.find(experiment_name, REDIS, request.args.get('version', None))
    except:
        abort(404)


app.secret_key = cfg.get('secret_key')
app.jinja_env.filters['number_to_percent'] = utils.number_to_percent
app.jinja_env.filters['number_format'] = utils.number_format


def start(environ, start_response):
    return app(environ, start_response)
