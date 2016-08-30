class Assessment:
    def __init__(self, index_id, query_id, assessor, document, grade):
        self.index_id = index_id
        self.query_id = query_id
        self.assessor = assessor
        self.document = document
        self.grade = grade

    def get_index_id(self):
        return self.index_id

    def get_query_id(self):
        return self.query_id

    def get_assessor(self):
        return self.assessor

    def get_document(self):
        return self.document

    def get_grade(self):
        return self.grade