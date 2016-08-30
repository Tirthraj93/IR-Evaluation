from dao import DAO
from models import Assessment


class Service:

    def __init__(self):
        pass

    def retrieve_documents(self, assessor, query_id, doc_retrieval_count):
        """
        Get documents documents from assessment index for given assessor and query id.
        If there aren't enough documents in assessor index, it will be fetched from crawled index.

        :param assessor: assessor id
        :param query_id: query id
        :param doc_retrieval_count: total docs to retrieve
        :return:
        """

        dao = DAO()

        if not dao.index_exists():
            dao.create_index()
            existing_doc_count = 0
        else:
            existing_doc_count = dao.get_doc_count(assessor, query_id)

        print 'existing count', existing_doc_count

        if existing_doc_count < doc_retrieval_count:
            dao.add_additional_docs(existing_doc_count, doc_retrieval_count, assessor, query_id)

        assessment_list = dao.retrieve_docs(assessor, query_id, doc_retrieval_count)

        doc_list = []

        for doc in assessment_list:

            doc_index_id = doc.get_index_id()
            doc_query_id = doc.get_query_id()
            doc_assessor_ = doc.get_assessor()
            doc_url = doc.get_document()
            doc_grade = doc.get_grade()

            doc_list.append({'index_id': doc_index_id,
                             'query_id': doc_query_id,
                             'assessor': doc_assessor_,
                             'document': doc_url,
                             'grade': doc_grade})

        return doc_list

    def store_assessment(self, assessment_list):
        dao = DAO()
        dao.store_assessment(assessment_list)

    def export_assessment(self, assessor):
        dao = DAO()
        dao.export_assessment(assessor)

    def store_results(self, result_size):
        dao = DAO()
        dao.store_results(result_size)

