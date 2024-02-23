import pandas as pd
import math

# Import the csv file
student_list = pd.read_csv('eleves/Anglais.csv', sep=';', skiprows=1, encoding = "ISO-8859-1")
student_list.columns = ['Nom', 'Prénom', 'Mail', 'Etat', 'Commencé', 'Terminé', 'Temps passé', 'Note']

def replace_commas_and_convert(value):
        # Replace the comma by a dot and convert a value into a float
        try:
            return float(value.replace(',', '.'))
        except ValueError:
            return value

student_list['Note'] = student_list['Note'].apply(replace_commas_and_convert)
print(student_list)

# Sort the dataframe by the grade
sorted_list = student_list.sort_values(by=student_list.columns[7])
print(sorted_list)

def groups_lv1(df, number_classes):
    students = len(df)
    number_students = students // number_classes
    rest = students // number_classes
    groups = pd.DataFrame()
    state = 0
    for j in range(number_classes):
        table = pd.DataFrame()
        if (rest!=0):
            number_students_real = number_students+1
            rest -= 1
        else:
            number_students_real = number_students
        for i in range(number_students_real):
            table = table.append(df.iloc[i+state])
        groups = groups.append(table)
        state = state + number_students_real
    return groups

groups = groups_lv1(sorted_list, 10)
print(groups)

"""
for group_num, group_df in groups.groupby("Numéro de groupe"):
    print(f"Groupe {group_num}:")
    print(group_df[["Prénom", "Nom", "Note"]].to_string(index=False))
    print()
for idx, group in enumerate(groups):
    print(f"Groupe {idx + 1}: {group}")
"""