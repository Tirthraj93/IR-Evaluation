from app.ManualAssessment.models import Assessment
import re

def write_assessment(path, assessment_list):

    print 'writing to file...'

    with open(path, 'w') as f:
        for item in assessment_list:
            out = "{} {} {} {}\n".format(item.get_query_id(), item.get_assessor(), item.get_document(),
                                         item.get_grade())
            f.write(out)


def write_lines(path, lines):

    print 'writing to file...'

    with open(path, 'w') as f:
        for line in lines:
            out = "{}\n".format(line)
            f.write(out)


def read_qrel(path):

    print 'reading qrel...'

    output = {}
    scores_list = []

    with open(path, 'r') as f:
        lines = f.read().splitlines()
        for line in lines:
            split_array = re.split('\\s+', line.strip())
            query_id = split_array[0]
            document = split_array[2]
            grade = split_array[3]

            scores_list.append(float(grade))

            current_dict = output.get(query_id, dict())
            current_dict[document] = float(grade)

            output[query_id] = current_dict

    sorted_scores = sorted(scores_list, reverse=True)

    return output


def read_results(results_path, qrel_data):

    print 'reading results...'

    temp_output = {}
    final_output = {}
    temp_scores = {}
    scores_output = {}

    with open(results_path, 'r') as f:
        lines = f.read().splitlines()

        for line in lines:
            split_array = line.strip().split(' ')
            query_id = split_array[0]
            document = split_array[2]
            rank = split_array[3]

            grade = qrel_data[query_id].get(document, 0.0)

            existing_data = temp_output.get(query_id, [])
            new_item = [document, int(rank)]
            existing_data.append(new_item)

            existing_scores = temp_scores.get(query_id, [])
            item = [document, grade]
            existing_scores.append(item)

            temp_output[query_id] = existing_data
            temp_scores[query_id] = existing_scores

        for key in temp_output:
            query_results = temp_output[key]
            query_scores = temp_scores[key]

            sorted_results = sorted(query_results, key=lambda x: x[1], reverse=False)[:1000]
            sorted_scores_list = sorted(query_scores, key=lambda x: x[1], reverse=True)

            # we don't need rank anymore
            # so let's leave it
            document_list = []
            for item in sorted_results:
                document_list.append(item[0])
            final_output[key] = document_list

            # we don't need score anymore
            # so let's leave it
            scores_list = []
            for item in sorted_scores_list:
                if document_list.__contains__(item[0]):
                    scores_list.append(item[0])
            scores_output[key] = scores_list

    return final_output, scores_output
