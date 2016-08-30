from elasticsearch import helpers
from django.utils.encoding import iri_to_uri

from app.Utilities.Constants import ASSESSMENT_INDEX, ASSESSMENT_TYPE, CREATE_ASSESSMENT
from app.Utilities.ElasticSearchUtility import ElasticSearchUtility
from app.Utilities.Constants import CRAWL_INDEX, CRAWL_TYPE, QUERY_MAP
from models import Assessment
from app.Utilities.FileUtility import write_assessment, write_lines
from app.Utilities.Constants import FILE_PATH, RESULTS_FILE

class DAO:
    def __init__(self):
        self.index = ASSESSMENT_INDEX
        self.index_type = ASSESSMENT_TYPE
        self.index_body = CREATE_ASSESSMENT
        self.es_util = ElasticSearchUtility()

    def index_exists(self):
        return self.es_util.index_exists(self.index)

    def create_index(self):
        self.es_util.create_index(self.index, self.index_body)

    def get_doc_count(self, assessor, query_id):
        """
        Gives total number of documents on assessment index for given assessor and query.
        :param assessor: the assessor
        :param query_id: the query to assess for
        :return: Total documents count for given assessor and query
        """
        print 'getting count...'
        es_client = self.es_util.es
        query = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "match": {
                                "assessor": assessor
                            }
                        },
                        {
                            "match": {
                                "query_id": query_id
                            }
                        }
                    ]
                }
            }
        }
        count = es_client.count(self.index, self.index_type, body=query)['count']
        print 'count - ', count
        return count

    def add_additional_docs(self, existing_doc_count, doc_retrieval_count, assessor, query_id):
        """
        add additional (doc_retrieval_count - existing_doc_count) documents from
        crawled index to assessment index for given assessor and query

        :param existing_doc_count:
        :param doc_retrieval_count:
        :param assessor:
        :param query_id:
        :return:
        """
        es_client = self.es_util.es
        query = QUERY_MAP[query_id]

        print 'adding additional docs...'

        additional_hits = self.__get_additional_docs(existing_doc_count, doc_retrieval_count, query)

        print 'total additional hits - ', len(additional_hits)

        bulk_actions = []
        index_meta = {
            "_index": self.index,
            "_type": self.index_type
        }

        doc_id = existing_doc_count + 1
        for hit in additional_hits:
            source_body = {
                "query_id": query_id,
                "assessor": assessor,
                "document": hit['_id'],
                "grade": 0
            }
            index_id = assessor + '_' + query_id + '_' + str(doc_id)
            index_meta.update({'_id': index_id, '_source': source_body})
            bulk_actions.append(index_meta)
            index_meta = {
                "_index": self.index,
                "_type": self.index_type
            }
            doc_id += 1
        print 'inserting - ', len(bulk_actions)
        helpers.bulk(es_client, bulk_actions)

    def retrieve_docs(self, assessor, query_id, doc_retrieval_count):
        es_client = self.es_util.es
        docs_list = []

        search = es_client.search(
            index=self.index,
            doc_type=self.index_type,
            scroll='10m',
            size=doc_retrieval_count,
            body={
                "query": {
                    "bool": {
                        "must": [
                            {
                                "match": {
                                    "assessor": assessor
                                }
                            },
                            {
                                "match": {
                                    "query_id": query_id
                                }
                            }
                        ]
                    }
                }
            })

        search_hits = search['hits']['hits']

        for hit in search_hits:
            docs_list.append(DAO.__hit_to_assessment(hit))

        return docs_list

    def __get_additional_docs(self, existing_doc_count, doc_retrieval_count, query):
        """
        Get additional (doc_retrieval_count - existing_doc_count) documents from
        crawled index

        :param existing_doc_count:
        :param doc_retrieval_count:
        :param query:
        :return:
        """
        additional_docs_count = doc_retrieval_count - existing_doc_count
        doc_hits = []

        es_client = self.es_util.es
        scroll = es_client.search(
            index=CRAWL_INDEX,
            doc_type=CRAWL_TYPE,
            scroll='10m',
            size=500,
            body={
                "query": {
                    "query_string": {
                        "default_field": "TEXT",
                        "query": query
                    }
                }
            })

        # retrieve results
        while len(doc_hits) < additional_docs_count:
            # skip first existing_doc_count results
            # prepare next scroll
            scroll_id = scroll['_scroll_id']
            # perform next scroll
            scroll = es_client.scroll(scroll_id=scroll_id, scroll='10m')
            # append hits
            doc_hits += scroll['hits']['hits']
            print 'got additional - ', len(doc_hits)

        return doc_hits[:additional_docs_count]

    @staticmethod
    def __hit_to_assessment(hit):

        index_id = hit['_id']
        query_id = iri_to_uri(hit['_source']['query_id'])
        assessor = iri_to_uri(hit['_source']['assessor'])
        document = iri_to_uri(hit['_source']['document'])
        grade = iri_to_uri(hit['_source']['grade'])

        assessment = Assessment(index_id, query_id, assessor, document, grade)

        return assessment

    def store_assessment(self, assessment_list):
        es_client = self.es_util.es
        for assessment in assessment_list:
            body = {
                "doc": {
                    "grade": str(assessment.get_grade())
                }
            }
            print 'updating ', assessment.get_index_id(), ' - ', assessment.get_grade()
            es_client.update(self.index, self.index_type, assessment.get_index_id(), body=body)

    def export_assessment(self, assessor):
        assessment_list = self.__retrieve_assessor_docs(assessor)

        path = FILE_PATH + assessor + '_qrel.txt'

        write_assessment(path, assessment_list)

    def __retrieve_assessor_docs(self, assessor):
        es_client = self.es_util.es
        docs_list = []

        search = es_client.search(
            index=self.index,
            doc_type=self.index_type,
            scroll='10m',
            size=600,
            body={
                "query": {
                    "match": {
                        "assessor": assessor
                    }
                }
            })

        search_hits = search['hits']['hits']

        print 'retrieved - ', len(search_hits)

        for hit in search_hits:
            docs_list.append(DAO.__hit_to_assessment(hit))

        return docs_list

    def store_results(self, result_size):
        output = []
        for query in QUERY_MAP:
            query_id = query
            query_code = 'Q' + str(query_id)
            author = 'Tirth'
            search_hits = self.__get_top_n(CRAWL_INDEX, CRAWL_TYPE, QUERY_MAP[query], result_size)
            rank = 1
            for hit in search_hits:
                document = iri_to_uri(hit['_id'])
                score = iri_to_uri(hit['_score'])
                output_line = query_id + ' ' + query_code + ' ' + document + ' ' + str(rank) + ' ' + str(score) + ' ' + author
                output.append(output_line)
                rank += 1
        write_lines(FILE_PATH + RESULTS_FILE, output)

    def __get_top_n(self, index_name, index_type, query, n):
        """
        Returns top n search hits from given index based on given query

        :param index_name: Name of the index
        :param index_type: Type of the index
        :param query: Query string
        :param n: Result size
        :return: Top n search hits
        """
        print 'fetching for - ', query
        es_client = self.es_util.es
        result = es_client.search(
            index=index_name,
            doc_type=index_type,
            size=n,
            fields=['_id', '_score'],
            body={
                "query": {
                    "query_string": {
                        "default_field": "TEXT",
                        "query": query
                    }
                }
            })
        return result['hits']['hits']