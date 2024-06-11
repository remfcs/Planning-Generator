####################################################################################
#                             Create Groups Functions                              #
####################################################################################
# Provides functionalities to create the groups of students                        #
####################################################################################

# --------------------------------------------------------------------------------
# Modules:
# --------------------------------------------------------------------------------
# 1. nomber_class_bis:
#    - Calcul the number of class mandatory for a number of student and a number of student max by class.
#
# 2. make_group:
#    - Create the balanced list of student for each groups fom a list a student and the number of group.
#
# 3. nomber_class:
#    - Calcul the number of class mandatory for a number of student based on the number of student available at the same time.
#
# 4. make_groups:
#    - Create the goups by calling the other function and fill them into the db.
#
# 5. make_association:
#    - Create the association between the groups, the teacher and the room.
#
# 6. get_students_per_SCHOOL_YEAR:
#    - basic function to balance the number of student in each group.
#
# 7. make_groups2:
#    - Create the balanced list of student for each groups fom a list a student and the number of group. (but with more simple approach)
#
# 8. make_groups_lv:
#    - Create the goups by calling the other function and fill them into the db.
# --------------------------------------------------------------------------------

# --------------------------------------------------------------------------------
# Dependencies:
# --------------------------------------------------------------------------------
# - sqlite3
# - algo_feature.database_function
# --------------------------------------------------------------------------------

import algo_feature.database_function as database_function
import sqlite3



def nomber_class_bis(nomber_student, nomber_by_class):
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

def nomber_class(sum, nb_students,  Data, students, promo_association,  max_by_class):
    lv = next(iter(students.keys()))
    list_slots = database_function.get_lv_slot(Data, promo_association)
    nb_slots = database_function.get_nb_available_teacher(Data, list_slots, lv)
    #print(nb_slots)
    nb_slots = round(nb_slots * nb_students / (sum + nb_students)) if round(nb_slots * nb_students / (sum + nb_students)) !=0 else 1
    #print(nb_slots)

    number_class = {}
    nb_students =0 
    for key, value in students.items():
        number_class[key] = 0
        nb_students += len(value)
    if len(number_class.keys()) == 1 :
        key = next(iter(number_class.keys()))
        number_class[key] = nb_slots
    else :
        for key, value in students.items():
            #number_class[key] = round(nb_slots * (len(value) / nb_students))
            number_class[key] = round(nb_slots * (len(value) / nb_students)) if round(nb_slots * (len(value) / nb_students)) != 0 else 1
            #print(number_class[key])
    # print(number_class)
    # def contains_only_3A(lst):
    #     return lst == ['3A']
    # if (contains_only_3A(promo_association)) & ((nomber_student / nomber_class) >= max_by_class):
    #     while (nomber_student / (nomber_class)) >= max_by_class:
    #         #nomber_class += 1
    return number_class

def make_groups(Data, promo_pair, max_by_class):
    conn = sqlite3.connect(Data)
    list_lv = database_function.find_list_lv(Data)
    while list_lv:
        print(list_lv)
        lv = list_lv.pop(0)
        deb = 0
        if '-débutant' in lv:
            lv = lv.split(' -débutant')[0]
            deb = 1
        promo_list = promo_pair[lv]
        if lv + " -débutant (jamais étudié)" in list_lv:
            list_lv.remove(lv + " -débutant (jamais étudié)")
            deb = 2
        promo_list = promo_pair[lv]
        
        slots = {}
        for promo_association in promo_list :
            list_slots = database_function.get_lv_slot(Data, promo_association)
            name = ', '.join(f"'{item}'" for item in promo_association)
            slots[name] = list_slots
        print(slots)

        inverse_slots = {}
        # Parcourir les éléments de slots
        for key, value in slots.items():
            # Convertir la liste en tuple pour l'utiliser comme clé dans inverse_slots (car les listes ne sont pas hashables)
            value_tuple = tuple(value)
            if value_tuple not in inverse_slots:
                inverse_slots[value_tuple] = []
            inverse_slots[value_tuple].append(key)
        print(inverse_slots)

        def get_students_and_nb_students(lv, promo_association):
            students = { }
            if deb ==0 :
                students[lv ] = []
            elif deb == 1 :
                students[lv + " -débutant (jamais étudié)"] = []
            elif deb == 2 :
                students[lv ] = []
                students[lv + " -débutant (jamais étudié)"] = []
            for promo in promo_association:
                for i in students :
                    if "-débutant (jamais étudié)" in i:
                        cursor = conn.cursor()
                        # Get the list of beginner students for the specific language and promo
                        cursor.execute("SELECT EMAIL FROM Student WHERE (LV1 = ? OR LV2 = ?) AND SCHOOL_YEAR = ?;",(i, i, promo))
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
                        cursor.execute(query, (i, i, i, i, promo))
                        student = cursor.fetchall()
                        student = [pos[0] for pos in student]  # Extract student emails

                    students[i] += student  # Add the students to the list
            nb_students =0 
            for key, value in students.items():
                nb_students += len(value)
                #print(lv, promo_association,f"Clé : {key}, Nombre d'éléments : {len(value)}")
            #print(promo_association, next(iter(students.keys())))
            return students, nb_students


        for promo_association in promo_list :
            sum = 0
            a = ', '.join(f"'{item}'" for item in promo_association)
            # Afficher les clés des éléments identiques
            print(promo_association, sum)
            for value_tuple, keys in inverse_slots.items():
                if  (len(keys) > 1) & (a in keys): 
                    print(a, keys, len(keys))
                    for i in keys:
                        association = [item.strip("'") for item in i.split(', ')]
                        print(association, promo_association)
                        if association != promo_association:  
                            st, nb = get_students_and_nb_students(lv, association)
                            sum += nb
            print(lv, promo_association, sum)

            students, nb_students = get_students_and_nb_students(lv, promo_association)
            print(promo_association, sum, nb_students)
            nb_class = nomber_class(sum,nb_students, Data, students, promo_association,  max_by_class)  # Calculate the number of classes needed
            print(nb_class)

            for key, value in nb_class.items():
                #print(key, value)
                students2 = students[key]
                groups = make_group(students2, value)  # Create groups based on the number of classes
                language = "_" + key[:3]  # Extract language abbreviation
                name = ""
                if "COMPLEMENTAIRE" in key or "DISPENSE" in key:
                    pass
                else :
                    if "-débutant (jamais étudié)" in key:
                        name = "_D"  # Append '_D' for beginner groups
                    if "COMPLEMENTAIRE" in key:
                        name = "_C"  # Append '_C' for complementary groups
                    i = 1
                    result_str = ', '.join(promo_association)  # Create a string representation of the promo list
                    #print(groups)
                    for group in groups:  # type: ignore
                        group_name = 'G' + str(i) + "_{" + result_str + "}" + language + name  # Create a unique group name
                        for student in group:
                            cursor = conn.cursor()
                            cursor.execute("INSERT INTO List_Groups_Students(ID_COURSE, ID_STUDENT) VALUES(?, ?);", (group_name, student))
                            conn.commit()  # Insert each student into the group and commit the changes
                        i += 1  # Increment the group counter

    conn.close()  # Close the database connection
    return
   
def make_association(Data, promo_pair):
    conn = sqlite3.connect(Data)  # Connect to the SQLite database
    for lv in promo_pair:
        promo_list = promo_pair[lv]
        slots = {}
        for promo_association in promo_list :
            insertions = []  # Initialize a list to store insertions

            list_slots = database_function.get_lv_slot(Data, promo_association)
            name = ', '.join(f"'{item}'" for item in promo_association)
            slots[name] = list_slots
            #print("\n" ,name,  lv, list_slots)
            teacher_availabilities = database_function.get_available_teacher2(Data, list_slots, lv)  # Get available teachers for the language
            #print(teacher_availabilities)            
            cursor = conn.cursor()
            pattern = '%{'+ ', '.join(promo_association) + "}_"+ lv[:3] + '%'  # Create a pattern to match courses for the language
            #print(pattern)
            cursor.execute("""
                           SELECT DISTINCT(ID_COURSE) FROM List_Groups_Students 
                           WHERE ID_COURSE LIKE ? ORDER BY LENGTH(ID_COURSE), ID_COURSE;""",
                            (pattern,))
            list_groups = cursor.fetchall()
            list_groups = [pos[0] for pos in list_groups]  # Extract course IDs
            #print(list_groups)
            for i in range(len(list_groups)):
                insertion = (teacher_availabilities[i][0], list_groups[i], teacher_availabilities[i][1], teacher_availabilities[i][0][4:])
                insertions.append(insertion)  # Prepare insertions of teacher and group associations
                cursor = conn.cursor()
                #print(teacher_availabilities[i][0],teacher_availabilities[i][1])
                cursor.execute("""
                                UPDATE Availability_Teachers SET ACTIVE = 1
                                WHERE ID_Availability LIKE ? AND ID_Teacher LIKE ?;
                               """, (teacher_availabilities[i][1],teacher_availabilities[i][0]))
                conn.commit()
            #print(insertions)
            final_insertions = insertions
            # final_insertions = []
            # for slot in list_slots:
            #     rooms_available = function_database.get_available_room(Data, slot)  # Get available rooms for the slot

            #     for i in range(len(insertions)):
            #         if insertions[i][2] == slot[0]:  # Match insertions with the current slot
            #             if rooms_available:
            #                 room = rooms_available.pop(0)  # Get the first available room and remove it from the list
            #             else:
            #                 room = ('No more available',)
            #             final_insertion = insertions[i] + room  # Add room information to the insertion
            #             final_insertions.append(final_insertion)  # Add to the final insertions list
            for value in final_insertions:
                result_str = ', '.join(promo_association)  # Create a string representation of the promo list
                cursor.execute("INSERT INTO Courses(LANGUAGE, ID_COURSE, ID_TEACHER, ID_AVAILABILITY, ID_ROOM, PROMO) VALUES(?, ?, ?, ?, ?, ?);", 
                            (value[3], value[1], value[0], value[2], "R pour le moment ", result_str))
                conn.commit()  # Insert the final insertion into the Courses table and commit the changes
    conn.close()    # Close the database connection

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
        slot_count = database_function.get_lv_slot(Data, promo_list)
        # slot_count correspond a tous les slots de cours disponible pour les langues (condition: meme slot dispo pour les 2 promos)
        list_lv = database_function.find_list_LV2(Data, promo_list)
        # list_lv2: liste de toutes les lv2 de la promo_list 
        list_lv1 = database_function.find_list_LV1(Data, promo_list)
        list_lv.append(list_lv1)
        for lv in list_lv:
            teacher_availabilities = database_function.get_available_teacher(Data, slot_count, lv)    
            #slot_nbr_for_lv: nbr de slot dispo pour une langue vivante
            #students_in_promo_pair = function_database.get_students_count(Data, promo_pair) 
            group = database_function.get_all_students_from_a_pair_and_lv(Data, promo_list, lv)
            language = "_"+lv[:3]
            name = ""
            total_student_studying_this_lv =  database_function.get_all_students_from_a_pair_studying_this_lv(Data, promo_list, lv)
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
                database_function.assigns_groups_to_students(Data, lv, group_name, group, teacher, slot)
                i+=1
        conn.close()
    return 

