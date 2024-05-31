import function_database
import sqlite3

def get_students_per_SCHOOL_YEAR(number_student, slot_nbr_for_lv):
    base_students_per_promo = number_student // slot_nbr_for_lv
    extra_students = number_student % slot_nbr_for_lv
    students_distribution = [base_students_per_promo] * slot_nbr_for_lv
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
        # slot_count correspond a tous les slots de cours disponible pour les langues (condition: meme slot dispo pour les 2 promos)
        list_lv = function_database.find_list_LV2(Data, promo_list)
        # list_lv2: liste de toutes les lv2 de la promo_list 
        list_lv.append("ANGLAIS")
        for lv in list_lv:
            teacher_availabilities = function_database.get_available_teacher(Data, slot_count, lv)    
            #slot_nbr_for_lv: nbr de slot dispo pour une langue vivante
            #students_in_promo_pair = function_database.get_students_count(Data, promo_pair) 
            group = function_database.get_all_students_from_a_pair_and_lv(Data, promo_list, lv)
            language = "_"+lv[:3]
            name = ""
            total_student_studying_this_lv =  function_database.get_all_students_from_a_pair_studying_this_lv(Data, promo_list, lv)
            if "-débutant (jamais étudié)" in lv :
                name = "_D"
            #nbr_slot = get_number_of_slot(total_student_studying_this_lv, len(teacher_availabilities), len(group))
            students_distribution = get_students_per_SCHOOL_YEAR(len(group), len(teacher_availabilities))
            
            groups = make_groups(group, students_distribution)
            i = 1
            for group in groups:
                group_name = 'G' + str(i) + language + name       #ESP D si débutant et promo
                teacher = teacher_availabilities[i-1][0]
                slot = teacher_availabilities[i-1][1]
                function_database.assigns_groups_to_students(Data, lv, group_name, group, teacher, slot)
                i+=1
        conn.close()
    return 
