import function_database
import sqlite3
import numpy as np

def get_students_per_class(number_student, number_by_class):
    students_per_class = 0
    # à expliquer 
    if (number_student % number_by_class) > ((number_student //number_by_class)*(2/3)) :
        students_per_class = number_student//number_by_class + 1
    else :
        students_per_class = number_student//number_by_class
    
    if  students_per_class == 0:
        students_per_class = 1
    return students_per_class

def make_groups(list_student, students_per_class):
    print(list_student)
    total_students = len(list_student)
    if total_students !=0:
        students_per_group = total_students // students_per_class
        extra_students = total_students % students_per_class
        # Nombre d'étudiants supplémentaires par groupe
        extra_per_group = [1 if i < extra_students else 0 for i in range(students_per_class)]
        groups = []
        start_idx = 0
        for i in range(students_per_class):
            # Nombre d'étudiants dans ce groupe
            group_size = students_per_group + extra_per_group[i]
            end_idx = start_idx + group_size
            groups.append(list_student[start_idx:end_idx])
            start_idx = end_idx
        return groups
    
    
def made_LV2_groupe(Data, list_forecast_by_promo, max_by_class):
    conn = sqlite3.connect(Data)
    for promo in function_database.find_list_CLASS(Data):
        nb_forecast = list_forecast_by_promo[promo]
        list_lv2 = function_database.find_list_LV2(Data, promo)
        for lv2 in list_lv2:
            students_in_promo = function_database.get_students_count(Data, promo) 
            print(promo, lv2)
            group = function_database.get_all_students_from_a_year_and_lv2(Data, promo, lv2) 
            ratio = len(group) / students_in_promo * nb_forecast
            rounded_ratio = round(ratio) 
            language = "_"+lv2[:3]
            if "-débutant (jamais étudié)" in lv2 :
                group = [pos[0] for pos in group]
            for i in range(rounded_ratio):
                name = ""
                if "-débutant (jamais étudié)" not in lv2 :
                    gaussienne_value = str(np.random.normal(mu, sigma))
                    name = "_D"
                group.append(('forecast',float(gaussienne_value)))       
            group = sorted(group, key=lambda x: x[1])
            nb_students = get_students_per_class(len(group), max_by_class)
            groups = make_groups(group, nb_students)
            i = 1
            for group in groups:
                group_name = 'G' + str(i) + language + name       #ESP D si débutant et promo
                function_database.assigns_groups_to_students(Data, promo, lv2, group_name, group)
                i+=1
        conn.close()
    return 
