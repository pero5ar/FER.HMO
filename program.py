import argparse
import csv


def parse_arguments():
    parse = argparse.ArgumentParser(
        description='',
        formatter_class=argparse.RawTextHelpFormatter)

    parse.add_argument(
        '-timeout', '--timeout',
        dest='timeout', required=True,
        help='Timeout.')

    parse.add_argument(
        '-award-activity', '--award-activity',
        dest='award_activity', required=True,
        help='Award activity.')

    parse.add_argument(
        '-award-student', '--award-student',
        dest='award_student', required=True,
        help='Award student.')

    parse.add_argument(
        '-minmax-penalty', '--minmax-penalty',
        dest='minmax_penalty', required=True,
        help='Minmax penalty.')

    parse.add_argument(
        '-students-file', '--students-file',
        dest='students_file', required=True,
        help='Students file.')

    parse.add_argument(
        '-requests-file', '--requests-file',
        dest='requests_file', required=True,
        help='Requests file.')

    parse.add_argument(
        '-overlaps-file', '--overlaps-file',
        dest='overlaps_file', required=True,
        help='Overlaps file.')

    parse.add_argument(
        '-limits-file', '--limits-file',
        dest='limits_file', required=True,
        help='Limits file.')

    args = parse.parse_args()
    return args


def parse_student_row(row):
    student = dict()
    student["student_id"] = row[0]
    student["activity_id"] = row[1]
    student["swap_weight"] = row[2]
    student["group_id"] = row[3]
    student["new_group_id"] = row[4]

    return student


def parse_request_row(row):
    request = dict()
    request["student_id"] = row[0]
    request["activity_id"] = row[1]
    request["req_group_id"] = row[2]

    return request


def parse_overlap_row(row):
    overlap = dict()
    overlap["group1_id"] = row[0]
    overlap["group2_id"] = row[1]

    return overlap


def parse_limit_row(row):
    limit = dict()
    limit["group_id"] = row[0]
    limit["students_cnt"] = row[1]
    limit["min_students"] = row[2]
    limit["min_preferred"] = row[3]
    limit["max_students"] = row[4]
    limit["max_preferred"] = row[5]

    return limit


# Testing:
def print_student_row(student):
    print(', '.join([student["student_id"], student["activity_id"], student["swap_weight"],
                     student["group_id"], student["new_group_id"]]))


def print_request_row(request):
    print(', '.join([request["student_id"], request["activity_id"], request["req_group_id"]]))


def print_overlap_row(overlap):
    print(', '.join([overlap["group1_id"], overlap["group2_id"]]))


def print_limit_row(limit):
    print(', '.join([limit["group_id"], limit["students_cnt"], limit["min_students"],
                     limit["min_preferred"], limit["max_students"], limit["max_preferred"]]))


def main():
    args = parse_arguments()

    timeout = args.timeout
    award_activity = args.award_activity
    award_student = args.award_student
    minmax_penalty = args.minmax_penalty

    students_file = args.students_file
    requests_file = args.requests_file
    overlaps_file = args.overlaps_file
    limits_file = args.limits_file

    students = []
    requests = []
    overlaps = []
    limits = []

    with open(students_file, newline='') as studentsCsvFile,\
            open(requests_file, newline='') as requestsCsvFile,\
            open(overlaps_file, newline='') as overlapsCsvFile,\
            open(limits_file, newline='') as limitsCsvFile:

        student_rows = csv.reader(studentsCsvFile, delimiter=',', quotechar='|')
        for row in student_rows:
            student = parse_student_row(row)
            students.append(student)

            print_student_row(student)

        request_rows = csv.reader(requestsCsvFile, delimiter=',', quotechar='|')
        for row in request_rows:
            request = parse_request_row(row)
            requests.append(request)

            print_request_row(request)

        overlap_rows = csv.reader(overlapsCsvFile, delimiter=',', quotechar='|')
        for row in overlap_rows:
            overlap = parse_overlap_row(row)
            overlaps.append(overlap)

            print_overlap_row(overlap)

        limit_rows = csv.reader(limitsCsvFile, delimiter=',', quotechar='|')
        for row in limit_rows:
            limit = parse_limit_row(row)
            limits.append(limit)

            print_limit_row(limit)

    print("Done")


main()
