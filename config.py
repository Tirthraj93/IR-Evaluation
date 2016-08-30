# Statement for enabling the development environment
DEBUG = True

# application directory
import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Storage Details
ES_HOST = dict(host="localhost", port=9200)

# Application threads
# THREADS_PER_PAGE = 2