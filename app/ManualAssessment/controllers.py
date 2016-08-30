from flask import Blueprint, render_template, request
from service import Service
from models import Assessment
from app.Utilities.Constants import RESULT_SIZE


# Define the blueprint: 'manual_assessment', set its url prefix: app.url/auth
manual_assessment = Blueprint('manual_assessment', __name__, url_prefix='/manual_assessment')


@manual_assessment.route('/', methods=['GET', 'POST'])
def assess():
    doc_list = []
    if request.method == 'POST':
        assessor = request.form['assessor']
        query_id = request.form['query_id']
        doc_retrieval_count = int(request.form['doc_count'])

        service = Service()
        doc_list = service.retrieve_documents(assessor, query_id, doc_retrieval_count)

    return render_template('ManualAssessment/manual_assessment.html', doc_list=doc_list)


@manual_assessment.route('/store', methods=['GET', 'POST'])
def store():
    request_type = request.form['button']
    if request_type == 'store_es':
        __store_to_es()
    else:
        __export_to_file()

    return render_template('ManualAssessment/manual_assessment.html', doc_list=[])


@manual_assessment.route('/store_results', methods=['GET', 'POST'])
def store_results():
    service = Service()
    service.store_results(RESULT_SIZE)
    return render_template('/index.html')


def __store_to_es():
    doc_size = int(request.form['doc_size']) + 1
    assessment_list = []

    for i in range(1, doc_size):
        index_id = request.form['index_id_' + str(i)]
        query_id = request.form['query_id_' + str(i)]
        assessor = request.form['assessor_' + str(i)]
        document = request.form['document_' + str(i)]
        grade = int(request.form['grade_' + str(i)])

        assessment = Assessment(index_id, query_id, assessor, document, grade)

        assessment_list.append(assessment)

    service = Service()
    service.store_assessment(assessment_list)


def __export_to_file():

    assessor = request.form['assessor_1'].split('_')[0]

    service = Service()
    service.export_assessment(assessor)