import argparse
import csv
import math
import random
from collections import deque
from time import time
from typing import Tuple, Dict, Set, List, Deque

program_start = time()

# Types and classes:

LookupTable = Dict[str, Set[str]]
MovesDict = Dict[Tuple[str, str], Deque[dict]]


class Constants:
    def __init__(self):
        self.timeout = 0
        self.award_activity: List[int] = []
        self.award_student = 0
        self.minmax_penalty = 0
        self.requests_set: Set[Tuple[str, str, str]] = set()
        self.request_groups: Dict[Tuple[str, str], Set(str)] = {}
        self.requested_activities_per_student: Dict[str, int] = {}
        self.overlaps_matrix: LookupTable = {}
        self.allowed_overlaps_by_student: Dict[str, Set[Tuple[str, str]]] = {}


class Variables:
    def __init__(self):
        self.student_activity_dict: Dict[Tuple[str, str], dict] = {}
        self.student_groups_dict: LookupTable = {}
        self.group_student_dict: LookupTable = {}
        self.moves: MovesDict = dict()
        self.groups_dict: Dict[str, dict] = {}
        self.global_moves_made: Set[Tuple[str, str]] = set()


# Parse:

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


# Print result

def print_result(variables: Variables):
    student_activity_rows = [[
        student["student_id"],
        student["activity_id"],
        student["swap_weight"],
        student["group_id"],
        student["new_group_id"] if student["new_group_id"] != student["group_id"] else "0"
    ] for student in variables.student_activity_dict.values()]
    with open('out.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["student_id", "activity_id", "swap_weight", "group_id", "new_group_id"])
        writer.writerows(student_activity_rows)


# Constraints:

# call before make move
def is_move_possible(student_id, old_group, new_group, student_groups: set, constants: Constants):
    overlaps_matrix = constants.overlaps_matrix
    allowed_overlaps_by_student = constants.allowed_overlaps_by_student
    if old_group["students_cnt"] <= old_group["min"] or new_group["students_cnt"] >= new_group["max"]:
        return False
    for group_id in student_groups:
        if group_id == old_group["group_id"] or group_id not in overlaps_matrix:
            continue
        if student_id in allowed_overlaps_by_student \
                and (group_id, new_group["group_id"]) in allowed_overlaps_by_student[student_id]:
            continue
        if new_group["group_id"] in overlaps_matrix[group_id]:
            return False
    return True


# call after make move
def is_state_possible(variables: Variables, constants: Constants):
    groups_dict = variables.groups_dict
    student_groups_dict = variables.student_groups_dict
    overlaps_matrix = constants.overlaps_matrix
    allowed_overlaps_by_student = constants.allowed_overlaps_by_student
    if any(group["students_cnt"] < group["min"] or group["students_cnt"] > group["max"]
           for group in groups_dict.values()):
        print("One group over or under capacity")
        return False
    for student_id, student_groups in student_groups_dict.items():
        checked = set()
        for group1_id in student_groups:
            checked.add(group1_id)
            for group2_id in student_groups:
                if group2_id in checked or group2_id not in overlaps_matrix:
                    continue
                if student_id in allowed_overlaps_by_student \
                        and (group1_id, group2_id) in allowed_overlaps_by_student[student_id]:
                    continue
                if group1_id in overlaps_matrix[group2_id]:
                    return False
    return True


def score_a(variables: Variables, constants: Constants):
    student_activity_dict = variables.student_activity_dict
    requests_set = constants.requests_set

    score = 0
    for (student_id, activity_id), student_activity in student_activity_dict.items():
        if student_activity["new_group_id"] != student_activity["group_id"] \
                and (student_id, activity_id, student_activity["new_group_id"]) in requests_set:
            score += student_activity["swap_weight"]
    return score


def score_b(variables: Variables, constants: Constants):
    student_activity_dict = variables.student_activity_dict
    award_activity = constants.award_activity

    activity_swaps_per_student = {}
    for (student_id, activity_id), student_activity in student_activity_dict.items():
        if student_id not in activity_swaps_per_student:
            activity_swaps_per_student[student_id] = set()
        if student_activity["new_group_id"] != student_activity["group_id"]:
            activity_swaps_per_student[student_id].add(activity_id)

    score = 0
    awards_number = len(award_activity)
    for activity_swaps in activity_swaps_per_student.values():
        swap_number = len(activity_swaps) - 1
        if swap_number == -1:
            continue
        if swap_number < awards_number:
            score += award_activity[swap_number]
        else:
            score += award_activity[-1]

    return score


def score_c(variables: Variables, constants: Constants):
    student_activity_dict = variables.student_activity_dict
    requests_set = constants.requests_set
    requested_activities_per_student = constants.requested_activities_per_student
    award_student = constants.award_student

    satisfied_activities_per_student: Dict[str, int] = {}
    for (student_id, activity_id), student_activity in student_activity_dict.items():
        if student_activity["new_group_id"] != student_activity["group_id"] \
                and (student_id, activity_id, student_activity["new_group_id"]) in requests_set:
            if student_id not in satisfied_activities_per_student:
                satisfied_activities_per_student[student_id] = 0
            satisfied_activities_per_student[student_id] += 1

    satisfied_students_counter = 0
    for student_id, activity_number in requested_activities_per_student.items():
        if student_id not in satisfied_activities_per_student:
            continue
        if satisfied_activities_per_student[student_id] == activity_number:
            satisfied_students_counter += 1

    return satisfied_students_counter * award_student


def score_d(variables: Variables, constants: Constants):
    groups_dict = variables.groups_dict
    minmax_penalty = constants.minmax_penalty
    return minmax_penalty * sum([group["min_preferred"] - group["students_cnt"]
                                 for group in groups_dict.values()
                                 if group["students_cnt"] < group["min_preferred"]])


def score_e(variables: Variables, constants: Constants):
    groups_dict = variables.groups_dict
    minmax_penalty = constants.minmax_penalty
    return minmax_penalty * sum([group["students_cnt"] - group["max_preferred"]
                                 for group in groups_dict.values()
                                 if group["students_cnt"] > group["max_preferred"]])


# Logic:

def make_move(student_id: str, activity_id: str, new_group_id: str, old_group_id: str, variables: Variables):
    variables.groups_dict[old_group_id]["students_cnt"] -= 1
    variables.groups_dict[new_group_id]["students_cnt"] += 1

    if len(variables.moves[(student_id, activity_id)]) == 1:
        variables.moves.pop((student_id, activity_id))  # it was the only one so no going back (unless undo)
    else:
        variables.moves[(student_id, activity_id)].remove(new_group_id)
        variables.moves[(student_id, activity_id)].append(old_group_id)

    variables.student_activity_dict[(student_id, activity_id)]["new_group_id"] = new_group_id
    variables.student_groups_dict[student_id].remove(old_group_id)
    variables.student_groups_dict[student_id].add(new_group_id)


def undo_move(student_id: str, activity_id: str, new_group_id: str, old_group_id: str, variables: Variables):
    variables.groups_dict[new_group_id]["students_cnt"] -= 1
    variables.groups_dict[old_group_id]["students_cnt"] += 1

    if (student_id, activity_id) not in variables.moves:
        variables.moves[(student_id, activity_id)] = deque()
    else:
        variables.moves[(student_id, activity_id)].remove(old_group_id)
    variables.moves[(student_id, activity_id)].append(new_group_id)

    variables.student_activity_dict[(student_id, activity_id)]["new_group_id"] = old_group_id
    variables.student_groups_dict[student_id].remove(new_group_id)
    variables.student_groups_dict[student_id].add(old_group_id)


def evaluate_move(student_id: str, activity_id: str, new_group_id: str,
                  moves_made: Set[Tuple[str, str]],  # only top loop can decide to go back
                  moves_sample: MovesDict,  # sample to evaluate the move on
                  variables: Variables, constants: Constants, depth: int):
    old_group_id: str = variables.student_activity_dict[(student_id, activity_id)]["new_group_id"]
    old_group = variables.groups_dict[old_group_id]
    new_group = variables.groups_dict[new_group_id]
    student_groups = variables.student_groups_dict[student_id]

    if depth == 0:
        if not is_move_possible(student_id, old_group, new_group, student_groups, constants):
            return None
        make_move(student_id, activity_id, new_group_id, old_group_id, variables)
        if not is_state_possible(variables, constants):
            undo_move(student_id, activity_id, new_group_id, old_group_id, variables)
            return None
        score = score_a(variables, constants) + score_b(variables, constants) + score_c(variables, constants) \
            - score_d(variables, constants) - score_e(variables, constants)
        undo_move(student_id, activity_id, new_group_id, old_group_id, variables)
        return score

    make_move(student_id, activity_id, new_group_id, old_group_id, variables)
    moves_made.add((student_id, activity_id))
    score = None
    for move_student_id, move_activity_id in moves_sample:
        if (move_student_id, move_activity_id) in moves_made:
            continue
        moves_copy = deque(variables.moves[(move_student_id, move_activity_id)])
        for move_group_id in moves_copy:
            move_score = evaluate_move(move_student_id, move_activity_id, move_group_id,
                                       set(moves_made), moves_sample,
                                       variables, constants, depth - 1)
            if move_score is None:
                continue
            if score is None or score < move_score:
                score = move_score
    undo_move(student_id, activity_id, new_group_id, old_group_id, variables)
    return move_score


def create_moves_sample(variables):
    moves_sample: MovesDict = dict()
    moves_key_list = list(variables.moves.keys())
    random_sample_max_size = 10 + int(math.sqrt(len(moves_key_list)))
    other_sample_max_size = 2 * random_sample_max_size

    # add if more than one free:
    i = 0
    for key, value in variables.moves.items():
        if i == other_sample_max_size:
            break
        for group_id in value:
            group = variables.groups_dict[group_id]
            if group["max"] - group["students_cnt"] >= 2:
                moves_sample[key] = value
                i += 1
                break

    # add randoms:
    for i in range(0, random_sample_max_size):
        key = random.choice(moves_key_list)
        if key not in variables.global_moves_made:
            moves_sample[key] = variables.moves[key]
    return moves_sample


def make_best_move(variables, constants):
    depth = 0
    best_score = None
    best_move = None

    subiteration = 0
    for student_id, activity_id in variables.moves:
        subiteration += 1
        if subiteration % 1000 == 0:
            print("subiteration no: ", subiteration, " - best score: ", best_score)
        if (student_id, activity_id) in variables.global_moves_made:
            continue
        moves_copy = deque(variables.moves[(student_id, activity_id)])
        for group_id in moves_copy:
            group = variables.groups_dict[group_id]
            if group["max"] <= group["students_cnt"]:
                continue  # skip full groups
            evaluation_sample = create_moves_sample(variables)
            if subiteration % 100 == 0:
                print(len(evaluation_sample))
            score = evaluate_move(student_id, activity_id, group_id,
                                  set(variables.global_moves_made), evaluation_sample,
                                  variables, constants, depth)
            if score is None:
                continue
            if best_score is None or best_score < score:
                best_score = score
                best_move = (student_id, activity_id, group_id)
            break   # a score is found, best to stop here

    if best_move is not None:
        student_id, activity_id, group_id = best_move
        old_group_id: str = variables.student_activity_dict[(student_id, activity_id)]["new_group_id"]
        make_move(student_id, activity_id, group_id, old_group_id, variables)
        variables.global_moves_made.add((student_id, activity_id))
    else:
        # no move found, try going back:
        for student_id, activity_id in variables.global_moves_made:
            if (student_id, activity_id) not in variables.moves:
                continue  # was the only option for that, not going back
            moves_copy = deque(variables.moves[(student_id, activity_id)])
            for group_id in moves_copy:
                evaluation_sample = create_moves_sample(variables)
                score = evaluate_move(student_id, activity_id, group_id,
                                      set(), evaluation_sample,
                                      variables, constants, depth)
                if score is None:
                    continue
                if best_score is None or best_score < score:
                    best_score = score
                    best_move = (student_id, activity_id, group_id)
        if best_move is not None:
            student_id, activity_id, group_id = best_move
            old_group_id: str = variables.student_activity_dict[(student_id, activity_id)]["new_group_id"]
            make_move(student_id, activity_id, group_id, old_group_id, variables)
            variables.global_moves_made.add((student_id, activity_id))


def main():
    args = parse_arguments()

    constants = Constants()
    variables = Variables()

    constants.timeout = int(args.timeout)
    constants.award_activity = [int(x) for x in args.award_activity.split(",")]
    constants.award_student = int(args.award_student)
    constants.minmax_penalty = int(args.minmax_penalty)

    students_file = args.students_file
    requests_file = args.requests_file
    overlaps_file = args.overlaps_file
    limits_file = args.limits_file

    student_activity_dict = variables.student_activity_dict
    student_groups_dict = variables.student_groups_dict
    group_student_dict = variables.group_student_dict
    requests_set = constants.requests_set
    moves = variables.moves
    request_groups = constants.request_groups
    requested_activities_per_student = constants.requested_activities_per_student
    overlaps_matrix = constants.overlaps_matrix
    allowed_overlaps_by_student = constants.allowed_overlaps_by_student
    groups_dict = variables.groups_dict

    with open(students_file, newline='') as studentsCsvFile, \
            open(requests_file, newline='') as requestsCsvFile, \
            open(overlaps_file, newline='') as overlapsCsvFile, \
            open(limits_file, newline='') as limitsCsvFile:

        limit_rows = csv.reader(limitsCsvFile, delimiter=',', quotechar='|')
        next(limit_rows)  # skip header
        for row in limit_rows:
            limit = parse_limit_row(row)
            group_id = limit["group_id"]
            groups_dict[group_id] = limit

        student_rows = csv.reader(studentsCsvFile, delimiter=',', quotechar='|')
        next(student_rows)  # skip header
        for row in student_rows:
            student = parse_student_row(row)
            if student["new_group_id"] == "0":
                student["new_group_id"] = student["group_id"]  # having 0 is the same as remaining in the same group
            student_id, activity_id, new_group_id = \
                student["student_id"], student["activity_id"], student["new_group_id"]

            student_activity_dict[(student_id, activity_id)] = student

            if student_id not in student_groups_dict:
                student_groups_dict[student_id] = set()
            student_groups_dict[student_id].add(new_group_id)
            if new_group_id not in group_student_dict:
                group_student_dict[new_group_id] = set()
            group_student_dict[new_group_id].add(student_id)

            if student["new_group_id"] != student["group_id"]:
                groups_dict[student["new_group_id"]]["students_cnt"] += 1
                groups_dict[student["group_id"]]["students_cnt"] -= 1

        request_rows = csv.reader(requestsCsvFile, delimiter=',', quotechar='|')
        next(request_rows)  # skip header
        for row in request_rows:
            request = parse_request_row(row)
            student_id, activity_id, req_group_id = \
                request["student_id"], request["activity_id"], request["req_group_id"]

            if (student_id, activity_id) not in student_activity_dict:
                continue  # zanemari zahtjeve kojih nema u student.csv

            requests_set.add((student_id, activity_id, req_group_id))

            if (student_id, activity_id) not in request_groups:
                request_groups[(student_id, activity_id)] = set()
                moves[(student_id, activity_id)] = deque()
                if student_id not in requested_activities_per_student:
                    requested_activities_per_student[student_id] = 0
                requested_activities_per_student[student_id] += 1
            request_groups[(student_id, activity_id)].add(req_group_id)
            moves[(student_id, activity_id)].append(req_group_id)

        overlap_rows = csv.reader(overlapsCsvFile, delimiter=',', quotechar='|')
        next(overlap_rows)  # skip header
        for row in overlap_rows:
            overlap = parse_overlap_row(row)
            group1_id, group2_id = overlap["group1_id"], overlap["group2_id"]
            if group1_id not in overlaps_matrix:
                overlaps_matrix[group1_id] = set()
            if group2_id not in overlaps_matrix:
                overlaps_matrix[group2_id] = set()
            overlaps_matrix[group1_id].add(group2_id)
            overlaps_matrix[group2_id].add(group1_id)
            if group1_id in group_student_dict and group2_id in group_student_dict:
                for student_id in group_student_dict[group1_id].intersection(group_student_dict[group2_id]):
                    if student_id not in allowed_overlaps_by_student:
                        allowed_overlaps_by_student[student_id] = set()
                    allowed_overlaps_by_student[student_id].add((group1_id, group2_id))
                    allowed_overlaps_by_student[student_id].add((group2_id, group1_id))

    iteration = 0
    algorithm_start = time()
    while time() < program_start + constants.timeout:
        print("-----------------------------------------------------------------------")
        make_best_move(variables, constants)
        iteration += 1
        print("-----------------------------------------------------------------------")

    print(iteration, " iterations took  ", time() - algorithm_start, " seconds.")

    print_start = time()
    print_result(variables)
    print("file write took: ", time() - print_start, " seconds.")

    a = score_a(variables, constants)
    b = score_b(variables, constants)
    c = score_c(variables, constants)
    d = score_d(variables, constants)
    e = score_e(variables, constants)

    score = score_a(variables, constants) + score_b(variables, constants) + score_c(variables, constants) \
        - score_d(variables, constants) - score_e(variables, constants)
    print("score is: ", score)

    print("program took: ", time() - program_start, " seconds")

main()
