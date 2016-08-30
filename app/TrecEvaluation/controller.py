from flask import Blueprint, render_template, request, jsonify

from app.Utilities.Constants import RESULTS_FILE
from service import Service

results_files = {'okapi_tf_results': 'okapi',
                 'tf_idf_results': 'tf_idf',
                 'bm25_results': 'bm25',
                 'laplace_uni_LM_results': 'laplace',
                 'jm_uni_lm_results': 'jm',
                 RESULTS_FILE: 'team',
                 'Trec-Text-long.txt': 'Test'}

qrel_files = {'qrels.adhoc.51-100.AP89.txt': 'trec_qrel',
              'qurel.1512.txt': 'team_qrel'}

# Define the blueprint: 'manual_assessment', set its url prefix: app.url/auth
trec_eval = Blueprint('trec_eval', __name__, url_prefix='/trec_eval')


@trec_eval.route('/', methods=['GET'])
def trec_evaluation():
    global results_files
    global qrel_files
    return render_template('TrecEvaluation/trec_eval.html',
                           results_files=results_files,
                           qrel_files=qrel_files,
                           evaluation={},
                           precision={},
                           recall={})


@trec_eval.route('/', methods=['GET', 'POST'])
def evaluate():
    global results_files
    global qrel_files

    qrel_file = request.form['qrel_file']
    results_file = request.form['results_file']
    show_query = False

    try:
        show_query = bool(request.form['show_query'])
    except:
        pass

    try:
        service = Service(qrel_file, results_file)
        evaluation = service.perform_evaluation(show_query)

        #array containing dictionary - query:[precision values]
        precision = service.get_precision()
        # array containing dictionary - query:[precision values]
        recall = service.get_recall()

        for key in precision:
            print key, ' - ', precision[key]

    except Exception as e:
        print type(e)
        return render_template('404.html'), 404

    return render_template('TrecEvaluation/trec_eval.html',
                           results_files=results_files,
                           qrel_files=qrel_files,
                           evaluation=evaluation,
                           precision=precision,
                           recall=recall)
