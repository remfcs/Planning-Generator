import pandas as pd
import csv

student_list = []

# Import the csv file
with open('eleves/csv/Anglais.csv', mode='r', newline='') as file:
    list = csv.reader(file, delimiter=';')
    next(list)
    for row in list:
        student = {
            'Nom': row[0],
            'Prénom': row[1],
            'Mail': row[2],
            'Note': row[7]
        }
        student_list.append(student)

print(student_list)

# Sort the dataframe by the grade
sorted_list = sorted(student_list, key = lambda x: x['Note'])
print(sorted_list)

def groups_lv1(list, number_classes):
    students = len(list)
    number_students = students // number_classes
    rest = students % number_classes
    groups = []
    state = 0
    for j in range(number_classes):
        if (rest!=0):
            number_students_real = number_students+1
            rest -= 1
        else:
            number_students_real = number_students
        group = list[state:number_students_real+state]
        groups.append(group)
        state = state + number_students_real
    return groups

groups = groups_lv1(sorted_list, 11)

for group in groups:
    print('Groupe', len(group))
    for student in group:
        print('Notes', student['Note'])
