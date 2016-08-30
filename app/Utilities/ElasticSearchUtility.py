from elasticsearch import Elasticsearch
from config import ES_HOST


class ElasticSearchUtility:
    """
    class to communicate with elasticsearch
    """

    def __init__(self):
        self.es = Elasticsearch(hosts=[ES_HOST], timeout=750)

    def index_exists(self, index_name):
        return self.es.indices.exists(index_name)

    def create_index(self, index_name, body):
        """
        Created a new index. If it already exists, deletes that first.

        :param index_name: index to create
        :param body: index creation body
        """
        if not self.es.indices.exists(index_name):
            print("creating '%s' index..." % index_name)
            res = self.es.indices.create(index=index_name, body=body)
            print(" response: '%s'" % res)

    def get_doc_count(self, index_name, index_type):
        """
        Get total number of documents in a given index

        :param index_name: name of the index
        :param index_type: type of the index
        :return: total number of documents
        """
        return self.es.count(index_name, index_type)