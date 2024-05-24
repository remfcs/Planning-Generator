import function_database
import sqlite3
import numpy as np

def get_students_per_class(number_student, slot_nbr_for_lv):
    base_students_per_class = number_student // slot_nbr_for_lv
    extra_students = number_student % slot_nbr_for_lv
    students_distribution = [base_students_per_class] * slot_nbr_for_lv
    for i in range(extra_students):
        students_distribution[i] += 1
    return students_distribution

def make_groups(list_student, students_distribution):
    groups = []
    start_index = 0
    for num_students in students_distribution:
        end_index = start_index + num_students
        group = list_student[start_index:end_index]
        groups.append(group)
        start_index = end_index
    
    return groups
    
    
def make_groups_lv(Data, promo_pair):
    conn = sqlite3.connect(Data)
    for promo_list in promo_pair:
        slot_count = function_database.get_lv_slot_count(Data, promo_list)
        list_lv2 = function_database.find_list_LV2(Data, promo_list)
        for lv2 in list_lv2:
            slot_nbr_for_lv, available_teacher = function_database.get_available_teacher(Data, slot_count, lv2)      
            #students_in_promo_pair = function_database.get_students_count(Data, promo_pair) 
            group = function_database.get_all_students_from_a_pair_and_lv2(Data, promo_list, lv2)
            #lv2_slot_count = function_database.get_lv2_slot_count(Data, lv2)
            language = "_"+lv2[:3]
            name = ""
            if "-débutant (jamais étudié)" in lv2 :
                group = [pos[0] for pos in group]
                name = "_D"   
            students_distribution = get_students_per_class(len(group),slot_nbr_for_lv)
            groups = make_groups(group, students_distribution)
            i = 1
            for group in groups:
                group_name = 'G' + str(i) + language + name       #ESP D si débutant et promo
                function_database.assigns_groups_to_students(Data, lv2, group_name, group)
                i+=1
        conn.close()
    return 
