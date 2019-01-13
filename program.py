import argparse
import csv
from typing import Dict, Set, List

LookupTable = Dict[str, Set[str]]


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
    student["swap_weight"] = int(row[2])
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
    limit["students_cnt"] = int(row[1])
    limit["min"] = int(row[2])
    limit["min_preferred"] = int(row[3])
    limit["max"] = int(row[4])
    limit["max_preferred"] = int(row[5])

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
    print(', '.join([limit["group_id"], limit["students_cnt"], limit["min"],
                     limit["min_preferred"], limit["max"], limit["max_preferred"]]))


# Constraints:

def is_possible(old_group, new_group, student_groups: set, overlaps_matrix: LookupTable):
    if old_group["students_cnt"] == old_group["min"] or new_group["students_cnt"] == new_group["max"]:
        return False
    for group_id in student_groups:
        if group_id == old_group[group_id]:
            continue
        if new_group["group_id"] in overlaps_matrix[group_id]:
            return False
    return True


def score_a(student_activity_dict, requests_set):
    score = 0
    for ((student_id, activity_id), student_activity) in student_activity_dict:
        if student_activity["new_group_id"] != 0 \
                and student_activity["new_group_id"] != student_activity["group_id"] \
                and (student_id, activity_id, student_activity["new_group_id"]) in requests_set:
            score += student_activity["swap_weight"]
    return score


def score_b(student_activity_dict, award_activity: List[int]):
    activity_swaps_per_student = {}
    for ((student_id, activity_id), student_activity) in student_activity_dict:
        if student_id not in activity_swaps_per_student:
            activity_swaps_per_student[student_id] = 0
        if student_activity["new_group_id"] != 0 \
                and student_activity["new_group_id"] != student_activity["group_id"]:
            activity_swaps_per_student[student_id] += 1

    score = 0
    awards_number = len(award_activity)
    for swap_number in activity_swaps_per_student.values():
        if swap_number < awards_number:
            score += award_activity[swap_number]
        else:
            score += award_activity[-1]

    return score


def score_c(student_activity_dict, requests_set, requested_activities_per_student: Dict[str, int], award_student):
    satisfied_activities_per_student: Dict[str, int] = {}
    for ((student_id, activity_id), student_activity) in student_activity_dict:
        if student_activity["new_group_id"] != 0 \
                and student_activity["new_group_id"] != student_activity["group_id"] \
                and (student_id, activity_id, student_activity["new_group_id"]) in requests_set:
            if student_id not in satisfied_activities_per_student:
                satisfied_activities_per_student[student_id] = 0
            satisfied_activities_per_student[student_id] += 1

    satisfied_students_counter = 0
    for (student_id, activity_number) in requested_activities_per_student:
        if satisfied_activities_per_student[student_id] == activity_number:
            satisfied_students_counter += 1

    return satisfied_students_counter * award_student


def score_d(groups_dict: dict, minmax_penalty):
    return minmax_penalty * sum([1 for group in groups_dict.values() if group["students_cnt"] < group["min_preferred"]])


def score_e(groups_dict: dict, minmax_penalty):
    return minmax_penalty * sum([1 for group in groups_dict.values() if group["students_cnt"] > group["max_preferred"]])


def main():
    args = parse_arguments()

    timeout = int(args.timeout)
    award_activity = [int(x) for x in args.award_activity.split(",")]
    award_student = int(args.award_student)
    minmax_penalty = int(args.minmax_penalty)

    students_file = args.students_file
    requests_file = args.requests_file
    overlaps_file = args.overlaps_file
    limits_file = args.limits_file

    student_activity_dict = {}  # will need to be updated every iteration
    student_groups_dict: LookupTable = {}   # will need to be updated every iteration
    requests_set = set()
    request_groups = {}
    requested_activities_per_student: Dict[str, int] = {}
    overlaps_matrix: LookupTable = {}
    groups_dict = {}    # will need to be updated every iteration

    with open(students_file, newline='') as studentsCsvFile,\
            open(requests_file, newline='') as requestsCsvFile,\
            open(overlaps_file, newline='') as overlapsCsvFile,\
            open(limits_file, newline='') as limitsCsvFile:

        student_rows = csv.reader(studentsCsvFile, delimiter=',', quotechar='|')
        next(student_rows)  # skip header
        for row in student_rows:
            student = parse_student_row(row)
            (student_id, activity_id) = (student["student_id"], student["activity_id"])

            student_activity_dict[(student_id, activity_id)] = student

            if student_id not in student_groups_dict:
                student_groups_dict[student_id] = set()
            student_groups_dict[student_id].add(student["group_id"])

        request_rows = csv.reader(requestsCsvFile, delimiter=',', quotechar='|')
        next(request_rows)  # skip header
        for row in request_rows:
            request = parse_request_row(row)
            (student_id, activity_id, req_group_id) = \
                (request["student_id"], request["activity_id"], request["req_group_id"])

            if (student_id, activity_id) not in student_activity_dict:
                continue    # zanemari zahtjeve kojih nema u student.csv

            requests_set.add((student_id, activity_id, req_group_id))

            if (student_id, activity_id) not in request_groups:
                request_groups[(student_id, activity_id)] = set()
                if student_id not in requested_activities_per_student:
                    requested_activities_per_student[student_id] = 0
                    requested_activities_per_student[student_id] += 1
            request_groups[(student_id, activity_id)].add(req_group_id)

        overlap_rows = csv.reader(overlapsCsvFile, delimiter=',', quotechar='|')
        next(overlap_rows)  # skip header
        for row in overlap_rows:
            overlap = parse_overlap_row(row)
            (group1_id, group2_id) = (overlap["group1_id"], overlap["group2_id"])
            if group1_id not in overlaps_matrix:
                overlaps_matrix[group1_id] = set()
            if group2_id not in overlaps_matrix:
                overlaps_matrix[group2_id] = set()
            overlaps_matrix[group1_id].add(group2_id)
            overlaps_matrix[group2_id].add(group1_id)

        limit_rows = csv.reader(limitsCsvFile, delimiter=',', quotechar='|')
        next(limit_rows)  # skip header
        for row in limit_rows:
            limit = parse_limit_row(row)
            groups_dict[limit["group_id"]] = limit

    print("Done")


main()
