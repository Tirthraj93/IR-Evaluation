from app.Utilities.FileUtility import read_qrel, read_results
from app.Utilities.Constants import FILE_PATH
from math import log

K_ARRAY = [5, 10, 15, 20, 30, 100, 200, 500, 1000]
K_RANGE = range(1, 1001)


class Service:
    def __init__(self, qrel_file, result_file):
        # get map as {query_id: {document: grade}} from qrel
        self.qrel_data = read_qrel(FILE_PATH + qrel_file)

        # get map as {query_id: array of documents} - in descending order
        self.results_data, self.sorted_scores = read_results(FILE_PATH + result_file, self.qrel_data)

        self.precision = dict()
        self.recall = dict()

    def get_precision(self):
        return self.precision

    def get_recall(self):
        return self.recall

    def perform_evaluation(self, show_query):
        all_precision_results = self.__precision_at_k()
        all_recall_results = self.__recall_at_k()
        avg_precision = self.__average_precision(all_precision_results)
        r_precision = self.__r_precision(all_precision_results)
        all_f1_results = self.__f1_at_k(all_precision_results, all_recall_results)
        all_ndcg_results = self.__ndcg_at_k()

        output_precision_results = self.__get_output_results(all_precision_results, k_array=K_RANGE,
                                                             heading="********Precision********",
                                                             variable=self.precision)
        output_avg_precision = self.__get_output_results(avg_precision, heading="********Average Precision********")
        output_r_precision_results = self.__get_output_results(r_precision, heading="********R-Precision********")
        output_recall_results = self.__get_output_results(all_recall_results, k_array=K_RANGE,
                                                          heading="********Recall********",
                                                          variable=self.recall)
        output_f1_results = self.__get_output_results(all_f1_results, k_array=K_RANGE, heading="********F1********")
        output_ndcg_precision = self.__get_output_results(all_ndcg_results, k_array=K_RANGE, heading="********nDCG********")

        temp_output = output_precision_results + output_avg_precision + output_r_precision_results \
                      + output_recall_results + output_f1_results + output_ndcg_precision

        if show_query:
            output = self.__output_measures(all_precision_results, all_recall_results, avg_precision, r_precision,
                                            all_f1_results, all_ndcg_results)
            output.append("Query ID: 25")
            output += temp_output
        else:
            output = temp_output



        return output

    def __ndcg_at_k(self):
        ndcg_at_k = dict()

        for query in self.results_data:
            # validate and get first rank
            rank_first_doc = self.results_data[query][0]
            score_first_doc = self.sorted_scores[query][0]

            query_results = self.results_data[query]
            query_results.__delitem__(0)

            dcg = self.qrel_data[query].get(rank_first_doc, 0.0)
            idcg = self.qrel_data[query].get(score_first_doc, 0.0)

            retrieved = 1.0

            for document in query_results:
                retrieved += 1

                qrel_key = self.qrel_data.get(query, {})

                dcg_result = qrel_key.get(document, 0.0)

                idcg_doc = self.sorted_scores[query][int(retrieved - 1.0)]
                idcg_result = qrel_key.get(idcg_doc, 0.0)

                dcg += dcg_result / log(retrieved, 2.0)
                idcg += idcg_result / log(retrieved, 2.0)

                ndcg = dcg / idcg

                current_dict = ndcg_at_k.get(query, dict())
                current_dict[retrieved] = ndcg

                ndcg_at_k[query] = current_dict

        return ndcg_at_k

    def __f1_at_k(self, all_precision_results, all_recall_results):
        f1_at_k = dict()

        for query in self.results_data:
            retrieved = 0.0
            for document in self.results_data[query]:
                retrieved += 1

                precision = all_precision_results[query][retrieved]
                recall = all_recall_results[query][retrieved]
                try:
                    f1 = (2.0 * precision * recall) / (precision + recall)
                except ZeroDivisionError:
                    f1 = 0.0

                current_dict = f1_at_k.get(query, dict())
                current_dict[retrieved] = f1

                f1_at_k[query] = current_dict

        return f1_at_k

    def __r_precision(self, all_precision_results):
        r_precision = dict()

        for query in self.results_data:
            total_relevant = self.__get_total_relevant(query)
            r_prec = all_precision_results[query][total_relevant]
            r_precision[query] = {"all": r_prec}

        return r_precision

    def __average_precision(self, all_precision_results):
        avg_precision = dict()

        for query in self.results_data:
            retrieved = 0.0
            precision_sum = 0.0
            total_relevant = self.__get_total_relevant(query)
            for document in self.results_data[query]:
                retrieved += 1
                if self.__is_relevant(query, document):
                    precision_sum += all_precision_results[query][retrieved]
            avg = precision_sum / total_relevant
            avg_precision[query] = {"all": avg}

        return avg_precision

    def __precision_at_k(self):
        precision_at_k = dict()

        for query in self.results_data:
            retrieved = 0.0
            retrieved_relevant = 0.0
            for document in self.results_data[query]:
                retrieved += 1
                if self.__is_relevant(query, document):
                    retrieved_relevant += 1
                precision = retrieved_relevant / retrieved

                current_dict = precision_at_k.get(query, dict())
                current_dict[retrieved] = precision

                precision_at_k[query] = current_dict

        return precision_at_k

    def __recall_at_k(self):
        recall_at_k = dict()

        for query in self.results_data:
            retrieved = 0.0
            retrieved_relevant = 0.0
            total_relevant = self.__get_total_relevant(query)

            for document in self.results_data[query]:
                retrieved += 1
                if self.__is_relevant(query, document):
                    retrieved_relevant += 1
                precision = retrieved_relevant / total_relevant

                current_dict = recall_at_k.get(query, dict())
                current_dict[retrieved] = precision

                recall_at_k[query] = current_dict

        return recall_at_k

    def __is_relevant(self, query, document):
        grade = self.qrel_data[query].get(document, 0)
        if grade >= 1:
            return True
        else:
            return False

    def __get_output_results(self, all_results, k_array=None, heading=None, query=None, variable=None):

        if k_array is None:
            k_array = ["all"]

        if heading is not None:
            output = [heading]
        else:
            output = []

        for element in k_array:

            measure_sum = 0.0

            if query is None:

                for q in self.results_data:
                    measure = all_results[q].get(element, 0)
                    measure_sum += measure

                measure = measure_sum / len(self.results_data)

                if variable is not None:
                    existing_content = variable.get('25', [])
                    existing_content.append(measure)

                    variable['25'] = existing_content

            else:
                measure = all_results[query].get(element, 0)
                if variable is not None:
                    existing_content = variable.get(query, [])
                    existing_content.append(measure)

                    variable[query] = existing_content

            if K_ARRAY.__contains__(element) or element == "all" :
                title = "  At " + repr(element).rjust(6) + " docs:\t"
                line = title + "%0.4f" % measure
                output.append(line)

        return output

    def __get_total_relevant(self, query):
        total_relevant = 0.0

        for document in self.results_data[query]:
            if self.__is_relevant(query, document):
                total_relevant += 1

        return total_relevant

    def __output_measures(self, all_precision_results, all_recall_results,
                          avg_precision, r_precision, all_f1_results, all_ndcg_results):
        output = []

        for query in self.results_data:
            output.append('Query ID: ' + query + '\n')

            output.append("********Precision********")
            result = self.__get_output_results(all_precision_results, k_array=K_RANGE, query=query,
                                               variable=self.precision)
            output += result

            output.append("********Average Precision********")
            result = self.__get_output_results(avg_precision, query=query)
            output += result

            output.append("********R-Precision********")
            result = self.__get_output_results(r_precision, query=query)
            output += result

            output.append("********nDCG********")
            result = self.__get_output_results(all_ndcg_results, k_array=K_RANGE, query=query)
            output += result

            output.append("********Recall********")
            result = self.__get_output_results(all_recall_results, k_array=K_RANGE, query=query, variable=self.recall)
            output += result

            output.append("********F1********")
            result = self.__get_output_results(all_f1_results, k_array=K_RANGE, query=query)
            output += result

            output.append("-----------------------------")
            output.append("\n\n")

        return output
