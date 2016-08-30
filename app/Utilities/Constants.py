from config import BASE_DIR

FILE_PATH = BASE_DIR + "\\Data\\"

RESULT_SIZE = 200
RESULTS_FILE = 'team_results.txt'

QUERY_MAP = {
    "151201": "picasso paintings",
    "151202": "brancusi sculptures",
    "151203": "barcelona gaudi architecture"
}

CRAWL_INDEX = "1512_great_mordenist_artist"
CRAWL_TYPE = "document"

ASSESSMENT_INDEX = "assessment"
ASSESSMENT_TYPE = "document"
CREATE_ASSESSMENT = {
    "settings": {
        "index": {
            "store": {
                "type": "default"
            },
            "number_of_shards": 3,
            "number_of_replicas": 0
        }
    },
    "mappings": {
        ASSESSMENT_TYPE: {
            "properties": {
                "query_id": {
                    "type": "string",
                    "store": "true",
                },
                "assessor": {
                    "type": "string",
                    "store": "true",
                },
                "document": {
                    "type": "string",
                    "store": "true",
                },
                "grade": {
                    "type": "string",
                    "store": "true",
                }
            }
        }
    },
    "analysis": {
        "analyzer": {
            "my_keyword": {
                "type": "keyword",
                "filter": "lowercase"
            }
        }
    }
}