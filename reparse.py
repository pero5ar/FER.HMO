import argparse
import csv
from typing import Tuple, Dict, Set, List, Deque


class Variables:
    def __init__(self):
        self.student_activity_dict: Dict[Tuple[str, str], dict] = {}


# Parse:

def parse_arguments():
    parse = argparse.ArgumentParser(
        description='',
        formatter_class=argparse.RawTextHelpFormatter)

    parse.add_argument(
        '-students-file', '--students-file',
        dest='students_file', required=True,
        help='Students file.')

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

# Print result

def print_result(variables: Variables, filename):
    student_activity_rows = [[
        student["student_id"],
        student["activity_id"],
        student["swap_weight"],
        student["group_id"],
        student["new_group_id"]
    ] for student in variables.student_activity_dict.values()]
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["student_id", "activity_id", "swap_weight", "group_id", "new_group_id"])
        writer.writerows(student_activity_rows)


def main():
    args = parse_arguments()

    variables = Variables()

    students_file = args.students_file

    student_activity_dict = variables.student_activity_dict

    with open(students_file, newline='') as studentsCsvFile:

        # Students file:

        student_rows = csv.reader(studentsCsvFile, delimiter=',', quotechar='|')
        next(student_rows)  # skip header
        for row in student_rows:
            student = parse_student_row(row)
            if student["new_group_id"] == "0":
                student["new_group_id"] = student["group_id"]  # having 0 is the same as remaining in the same group
            student_id, activity_id, new_group_id = \
                student["student_id"], student["activity_id"], student["new_group_id"]

            # Constants calculation:

            student_activity_dict[(student_id, activity_id)] = student

    print_result(variables, 'r_output.csv')

main()
