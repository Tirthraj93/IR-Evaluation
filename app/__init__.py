# Import flask and template operators
from flask import Flask, render_template

# Define the WSGI application object
app = Flask(__name__)


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


@app.route('/')
def home():
    return render_template('index.html')

# Import a module / component using its blueprint handler variable (mod_auth)
from app.ManualAssessment.controllers import manual_assessment
from app.TrecEvaluation.controller import trec_eval

# Register blueprint(s)
app.register_blueprint(manual_assessment)
app.register_blueprint(trec_eval)