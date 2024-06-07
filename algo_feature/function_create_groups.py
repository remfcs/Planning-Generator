import algo_feature.function_database as function_database
import sqlite3

""" 
Refaire 'nomber_class' en calculant le nb de prof dispo afin 



"""

def nomber_class(nomber_student, nomber_by_class):
    nomber_class = 0
    # à expliquer 
    if (nomber_student % nomber_by_class) > ((nomber_student //nomber_by_class)*(2/3)) :
        nomber_class = nomber_student//nomber_by_class + 1
    else :
        nomber_class = nomber_student//nomber_by_class
    
    if  nomber_class == 0:
        nomber_class = 1
    return nomber_class


def make_group(list_student, number_class):
    total_students = len(list_student)  # Calculate the total number of students
    if total_students != 0:  # Proceed if there are students
        students_per_group = total_students // number_class  # Calculate the base number of students per group
        extra_students = total_students % number_class  # Calculate the number of extra students that don't fit evenly

        # List indicating which groups will have an extra student
        extra_per_group = [1 if i < extra_students else 0 for i in range(number_class)]

        groups = []  # Initialize the list of groups
        start_idx = 0  # Starting index for slicing the list of students

        for i in range(number_class):
            group_size = students_per_group + extra_per_group[i]  # Calculate the size of the current group
            end_idx = start_idx + group_size  # Calculate the ending index for the current group
            groups.append(list_student[start_idx:end_idx])  # Slice the list of students and add the group to the list of groups
            start_idx = end_idx  # Update the starting index for the next group

        return groups  # Return the list of groups

def make_groups(Data, promo_pair, nb_by_class):
    conn = sqlite3.connect(Data)  # Connect to the SQLite database
    for promo_list in promo_pair:
        list_lv2 = function_database.find_list_LV2(Data, promo_list)  # Get list of LV2 languages for the promo list
        list_lv1 = function_database.find_list_LV1(Data, promo_list)  # Get list of LV1 languages for the promo list
        list_lv = list_lv1 + list_lv2  # Combine both lists of languages

        for lv in list_lv:
            students = []
            for promo in promo_list:
                if "-débutant (jamais étudié)" in lv:
                    cursor = conn.cursor()
                    # Get the list of beginner students for the specific language and promo
                    cursor.execute("SELECT EMAIL FROM Student WHERE (LV1 = ? OR LV2 = ?) AND SCHOOL_YEAR = ?;", (lv, lv, promo))
                    student = cursor.fetchall()
                    student = [pos[0] for pos in student]  # Extract student emails
                else:
                    cursor = conn.cursor()
                    query = """
                    SELECT EMAIL, 
                        CASE 
                            WHEN LV1 = ? THEN GRADE_LV1 
                            WHEN LV2 = ? THEN GRADE_LV2 
                        END AS GRADE 
                    FROM Student 
                    WHERE (LV1 = ? OR LV2 = ?) AND SCHOOL_YEAR = ?
                    ORDER BY GRADE DESC;
                    """
                    # Get the list of non-beginner students sorted by their grades for the specific language and promo
                    cursor.execute(query, (lv, lv, lv, lv, promo))
                    student = cursor.fetchall()
                    student = [pos[0] for pos in student]  # Extract student emails

                students += student  # Add the students to the list

            nb_class = nomber_class(len(students), nb_by_class)  # Calculate the number of classes needed
            groups = make_group(students, nb_class)  # Create groups based on the number of classes

            language = "_" + lv[:3]  # Extract language abbreviation
            name = ""
            if "-débutant (jamais étudié)" in lv:
                name = "_D"  # Append '_D' for beginner groups

            i = 1
            result_str = ', '.join(promo_list)  # Create a string representation of the promo list

            for group in groups:  # type: ignore
                group_name = 'G' + str(i) + "_{" + result_str + "}" + language + name  # Create a unique group name
                for student in group:
                    cursor.execute("INSERT INTO List_Groups_Students(ID_COURSE, ID_STUDENT) VALUES(?, ?);", (group_name, student))
                    conn.commit()  # Insert each student into the group and commit the changes
                i += 1  # Increment the group counter

    conn.close()  # Close the database connection
    return

def make_association(Data, promo_pair):
    conn = sqlite3.connect(Data)  # Connect to the SQLite database
    for promo_list in promo_pair:
        list_slots = function_database.get_lv_slot_count(Data, promo_list)  # Get the list of slots for the promo list
        list_lv2 = function_database.find_list_LV2(Data, promo_list)  # Get list of LV2 languages for the promo list
        list_lv1 = function_database.find_list_LV1(Data, promo_list)  # Get list of LV1 languages for the promo list
        list_lv = list_lv1 + list_lv2  # Combine both lists of languages
        list_lv_check = []  # Initialize a list to keep track of checked languages
        insertions = []  # Initialize a list to store insertions
        final_insertions = []  # Initialize a list to store final insertions

        for lv in list_lv:
            lv_bis = lv
            if '-débutant' in lv_bis:
                lv_bis = lv_bis.split(' -débutant')[0]  # Remove '-débutant' suffix for comparison

            if lv_bis not in list_lv_check:
                teacher_availabilities = function_database.get_available_teacher2(Data, list_slots, lv_bis)  # Get available teachers for the language
                list_lv_check.append(lv_bis)  # Mark the language as checked

                cursor = conn.cursor()
                pattern = '%' + lv_bis[:3] + '%'  # Create a pattern to match courses for the language
                cursor.execute("SELECT DISTINCT(ID_COURSE) FROM List_Groups_Students WHERE ID_COURSE LIKE ? ORDER BY LENGTH(ID_COURSE), ID_COURSE;", (pattern,))
                list_groups = cursor.fetchall()
                list_groups = [pos[0] for pos in list_groups]  # Extract course IDs

                if len(teacher_availabilities) > len(list_groups):
                    print("teacher_availabilities > list_groups")
                elif len(teacher_availabilities) < len(list_groups):
                    print("teacher_availabilities < list_groups")
                else:
                    for i in range(len(teacher_availabilities)):
                        insertion = (teacher_availabilities[i][0], list_groups[i], teacher_availabilities[i][1], teacher_availabilities[i][0][4:])
                        insertions.append(insertion)  # Prepare insertions of teacher and group associations

        for slot in list_slots:
            rooms_available = function_database.get_available_room(Data, slot)  # Get available rooms for the slot

            for i in range(len(insertions)):
                if insertions[i][2] == slot[0]:  # Match insertions with the current slot
                    if rooms_available:
                        room = rooms_available.pop(0)  # Get the first available room and remove it from the list
                    else:
                        room = ('No more available',)
                    final_insertion = insertions[i] + room  # Add room information to the insertion
                    final_insertions.append(final_insertion)  # Add to the final insertions list

        for value in final_insertions:
            result_str = ', '.join(promo_list)  # Create a string representation of the promo list
            cursor.execute("INSERT INTO Courses(LANGUAGE, ID_COURSE, ID_TEACHER, ID_AVAILABILITY, ID_ROOM, PROMO) VALUES(?, ?, ?, ?, ?, ?);", 
                           (value[3], value[1], value[0], value[2], value[4], result_str))
            conn.commit()  # Insert the final insertion into the Courses table and commit the changes

    conn.close()  # Close the database connection





"""

Anciennes fonctions 

"""
def get_students_per_SCHOOL_YEAR(number_student, slot_nbr_for_lv):
    base_students_per_promo = number_student // slot_nbr_for_lv
    extra_students = number_student % slot_nbr_for_lv
    students_distribution = [base_students_per_promo] * slot_nbr_for_lv
    for i in range(extra_students):
        students_distribution[i] += 1
    return students_distribution

def make_groups2(list_student, students_distribution):
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
        list_lv1 = function_database.find_list_LV1(Data, promo_list)
        list_lv.append(list_lv1)
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
            
            groups = make_groups2(group, students_distribution)
            i = 1
            for group in groups:
                group_name = 'G' + str(i) + language + name       #ESP D si débutant et promo
                teacher = teacher_availabilities[i-1][0]
                slot = teacher_availabilities[i-1][1]
                function_database.assigns_groups_to_students(Data, lv, group_name, group, teacher, slot)
                i+=1
        conn.close()
    return 

