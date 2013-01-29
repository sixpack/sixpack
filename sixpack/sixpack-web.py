from flask import Flask, render_template
import db
from models import Experiment

app = Flask(__name__)



# List of experiments
@app.route("/")
def hello():
    experiments = Experiment.all(db.REDIS)
    for experiment in experiments:
        print dir(experiment)
    return render_template('dashboard.html')

# Details for experiment
@app.route("/experiment/<experiment_name>/")
def details(experiment_name):
    pass

# Set winner for an experiment
@app.route("/experiment/<experiment_name>/winner/", methods=['POST'])
def set_winner(experiment_name):
    pass

# Reset experiment
@app.route("/experiment/<experiment_name>/reset/", methods=['POST'])
def reset_experiment(experiment_name):
    pass

# Reset experiment winner
@app.route("/experiment/<experiment_name>/winner/reset/", methods=['POST'])
def reset_winner(experiment_name):
    pass

# Delete experiment
@app.route("/experiment/<experiment_name>/delete/", methods=['DELETE'])
def delete_experiment(experiment_name):
    pass

# Archive experiment
@app.route("/experiment/<experiment_name>/archive", methods=['POST'])
def archive_experiment(archive_experiment):
    pass

@app.route('/favicon.ico')
def favicon():
    return ''

if __name__ == "__main__":
    app.run(port=5001, debug=True)