import sqlite3
import re


def get_students_with_schedule_conflicts(Data):
    conn = sqlite3.connect(Data)
    cursor = conn.cursor()
    # Get students and their courses along with the course availability
    query = """
        SELECT 
            lgs1.ID_STUDENT,
            c1.ID_AVAILABILITY,
            c1.ID_GROUP AS COURSE_1,
            c2.ID_GROUP AS COURSE_2
        FROM 
            List_Groups_Students lgs1
        JOIN 
            (SELECT ID_GROUP, ID_AVAILABILITY FROM Courses ORDER BY LENGTH(ID_GROUP), ID_GROUP) AS c1 ON lgs1.ID_COURSE = c1.ID_GROUP
        JOIN 
            List_Groups_Students lgs2 ON lgs1.ID_STUDENT = lgs2.ID_STUDENT
        JOIN 
            Courses c2 ON lgs2.ID_COURSE = c2.ID_GROUP
        WHERE 
            c1.ID_AVAILABILITY = c2.ID_AVAILABILITY
            AND c1.ID_GROUP != c2.ID_GROUP
            AND c1.ID_GROUP < c2.ID_GROUP
        ORDER BY 
            c1.ID_AVAILABILITY, LENGTH(c1.ID_GROUP), c1.ID_GROUP;
            """
    cursor.execute(query)
    conflicts = cursor.fetchall()
    conn.close()
    processed_conflicts = []
    for conflict in conflicts:
        student_id, availability, course_1, course_2 = conflict
        if course_1.endswith('_ANG'):
            processed_conflicts.append((student_id, availability, course_1, course_2))
        elif course_2.endswith('_ANG'):
            processed_conflicts.append((student_id, availability, course_2, course_1))
        else:
            processed_conflicts.append((student_id, availability, course_1, course_2))
 
    def sort_key(x):
        availability, course_1, _ = x[1:4]
        match = re.search(r'G(\d+)_', course_1)
        course_num = int(match.group(1)) if match else float('inf')
        return (availability, course_num, course_1)

    processed_conflicts.sort(key=sort_key)
    return processed_conflicts

def get_list_group(Data, language, promo_list):
    conn = sqlite3.connect(Data)
    cursor = conn.cursor()
    #print(promo_list)
    result_str = '%' +', '.join(promo_list)+ '%'
    cursor.execute("SELECT ID_GROUP FROM Courses WHERE LANGUAGE LIKE ? AND ID_GROUP like ?;",(language, result_str,))
    result = cursor.fetchall()
    conn.close()
    return len(result)

def get_promo_list(Data, id_availability, id_group):
    conn = sqlite3.connect(Data)
    cursor = conn.cursor()
    cursor.execute("SELECT PROMO FROM Courses WHERE ID_GROUP LIKE ? AND ID_AVAILABILITY LIKE ?;", (id_group, id_availability,))
    result = cursor.fetchall()
    conn.close()
    return result[0][0]


def resolution_conflict(Data):
    conflicts = get_students_with_schedule_conflicts(Data)
    for conflict in conflicts:
        new_group = get_new_group(Data, conflict[2])
        conn = sqlite3.connect(Data)
        cursor = conn.cursor()
        #print(new_group, conflict[0], conflict[2])
        cursor.execute("UPDATE List_Groups_Students SET ID_COURSE = ? WHERE ID_STUDENT LIKE ? AND ID_COURSE LIKE ?;", ( new_group, conflict[0], conflict[2]))
        conn.commit()
        conn.close()
    return

#print(resolution_conflict('data/test.sqlite3'))

def get_nb_student_by_group(Data):
    conn = sqlite3.connect(Data)
    cursor = conn.cursor()
    query = """
        SELECT lst.ID_COURSE, COUNT(lst.ID_STUDENT)
        FROM List_Groups_Students AS lst
        WHERE lst.ID_COURSE LIKE '%ANG'
        GROUP BY lst.ID_COURSE
        ORDER BY LENGTH(lst.ID_COURSE), lst.ID_COURSE;
    """
    cursor.execute(query) # Added comma to create a tuple with a single element
    result = cursor.fetchall()
    conn.close()
    return result


def get_list_stutents_from_group(Data, id_group):
    conn = sqlite3.connect(Data)
    cursor = conn.cursor()
    query = """
        SELECT ID_STUDENT FROM List_Groups_Students WHERE ID_COURSE LIKE ?;
    """
    cursor.execute(query, (id_group,)) # Added comma to create a tuple with a single element
    result = cursor.fetchall()
    conn.close()    
    return result

def get_new_group(Data, id_group):
    match = re.search(r'G(\d+)_', id_group)
    after_underscore = id_group[id_group.index('_'):]
    promo_list = id_group.split('_')[1]
    language =  id_group.split('_')[2]
    if match:
        value_between_G_and_underscore = match.group(1)
    if int(value_between_G_and_underscore) % 2 == 0:
        if int(value_between_G_and_underscore)==get_list_group(Data, language, promo_list):
            new_group = "G" + str(int(value_between_G_and_underscore) + 1) + after_underscore
        else :
            new_group = "G" + str(int(value_between_G_and_underscore) - 1) + after_underscore
    elif int(value_between_G_and_underscore) % 2 == 1:
        if int(value_between_G_and_underscore)==get_list_group(Data, language, promo_list):
            new_group = "G" + str(int(value_between_G_and_underscore) - 1) + after_underscore
        else:
            new_group = "G" + str(int(value_between_G_and_underscore) + 1) + after_underscore
    return new_group

def balance_groups(Data, max_by_class):
    list_groups = get_nb_student_by_group(Data)
    for group in list_groups:
        if group[1] > max_by_class :
            n = group[1]  - max_by_class
            list_students = get_list_stutents_from_group(Data, group[0])
            students = list_students[:n//2]
            new_group = get_new_group(Data, group[0])
            conn = sqlite3.connect(Data)
            for student in students:
                cursor = conn.cursor()
                #print(new_group, student[0], group[0])
                cursor.execute("UPDATE List_Groups_Students SET ID_COURSE = ? WHERE ID_STUDENT LIKE ? AND ID_COURSE LIKE ?;", ( new_group, student[0], group[0]))
                conn.commit()
            conn.close()
    return


def resolution_conflict_inverse(Data):
    conflicts = get_students_with_schedule_conflicts(Data)
    for conflict in conflicts:
        new_group = get_new_group_inverse(Data, conflict[2])
        conn = sqlite3.connect(Data)
        cursor = conn.cursor()
        #print(new_group, conflict[0], conflict[2])
        cursor.execute("UPDATE List_Groups_Students SET ID_COURSE = ? WHERE ID_STUDENT LIKE ? AND ID_COURSE LIKE ?;", ( new_group, conflict[0], conflict[2]))
        conn.commit()
        conn.close()
    return

def get_new_group_inverse(Data, id_group):
    match = re.search(r'G(\d+)_', id_group)
    after_underscore = id_group[id_group.index('_'):]
    promo_list = id_group.split('_')[1]
    language =  id_group.split('_')[2]
    if match:
        value_between_G_and_underscore = match.group(1)
    if int(value_between_G_and_underscore) % 2 == 0:
        if int(value_between_G_and_underscore)==get_list_group(Data, language, promo_list):
            new_group = "G" + str(int(value_between_G_and_underscore) + 1) + after_underscore
        else :
            new_group = "G" + str(int(value_between_G_and_underscore) + 1) + after_underscore
    elif int(value_between_G_and_underscore) % 2 == 1:
        if int(value_between_G_and_underscore)==get_list_group(Data, language, promo_list):
            new_group = "G" + str(int(value_between_G_and_underscore) - 1) + after_underscore
        else:
            new_group = "G" + str(int(value_between_G_and_underscore) - 1) + after_underscore
    return new_group
