####################################################################################
#                                Database Functions                                #
####################################################################################
# Provides functionalities to interact with the SQLite database, including         #
# deleting table data, inserting data frames into tables, and retrieving specific  #
# lists and information based on queries.                                          #
####################################################################################

# --------------------------------------------------------------------------------
# Modules:
# --------------------------------------------------------------------------------
# 1. delete_table_data:
#    - Deletes all data from a specified table.
#
# 2. insert_df_into_db:
#    - Inserts a DataFrame into a specified table in the database.
#
# 3. find_list_SCHOOL_YEAR:
#    - Retrieves a list of distinct school years from the Student table.
#
# 4. find_list_LV2:
#    - Retrieves a list of distinct LV2 (language) options for specified school years.
#
# 5. find_list_LV1:
#    - Retrieves a list of distinct LV1 (language) options for specified school years.
#
# 6. find_list_lv:
#   - Retrieves a list of all distinct LV (language) from the database.
#
# 7. get_all_students_from_a_pair_and_lv:
#   - 
#
# 8. get_all_students_from_a_pair_studying_this_lv:
#   - 
#
# 9. assigns_groups_to_students:
#   - Inserts a combinaison of id group and id student into a specified table in the database.
#
# 10. get_students_count:
#   - Retrieves the number of student for a specified school years.
#
# 11. get_lv_slot:
#   - Retrieves the list of slot for specified school years.
#
# 12. get_available_teacher:
#   - Retrieves the list of available teachers for a given slot and language.
#
# 13. get_nb_available_teacher.
#   - Retrieves the number of available teachers for a given slot and language.
#
# 14. get_available_teacher2:
#   - Retrieves the list of available teachers for given slots and language.
#
# 15. get_available_room:
#   - Retrieves the list of available rooms for given slots.
# --------------------------------------------------------------------------------

# --------------------------------------------------------------------------------
# Dependencies:
# --------------------------------------------------------------------------------
# - sqlite3
# --------------------------------------------------------------------------------

import sqlite3

def delete_table_data(filename, table):
    # Connexion à la base de données
    conn = sqlite3.connect(filename)
    cursor = conn.cursor()
    # Exécution de la requête SQL pour supprimer toutes les lignes de la table spécifiée
    cursor.execute("DELETE FROM '" + table + "';")
    # Commit des changements dans la base de données
    conn.commit() 
    # Fermeture de la connexion à la base de données
    conn.close()
    # La fonction ne retourne rien, elle modifie la base de données directement
 
def insert_df_into_db(conn, students_info, table):
    conn.cursor()
    students_info.to_sql(table, conn, if_exists='append', index=False)
    conn.close()
    
def find_list_SCHOOL_YEAR(Data):
    conn = sqlite3.connect(Data)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT(SCHOOL_YEAR) FROM Student;")
    list_SCHOOL_YEAR = cursor.fetchall()
    list_SCHOOL_YEAR = [row[0] for row in list_SCHOOL_YEAR]
    list_Class = cursor.fetchall()
    list_Class = [row[0] for row in list_Class]
    conn.close()
    return list_SCHOOL_YEAR

def find_list_LV2(Data, promo_pair):
    conn = sqlite3.connect(Data)
    cursor = conn.cursor()
    list_lv2 = []
    for promo in promo_pair:
        cursor.execute("SELECT DISTINCT(LV2) FROM Student WHERE SCHOOL_YEAR = '" + promo + "';")
        lv2_results = cursor.fetchall()
        for lv2_row in lv2_results:
            if lv2_row[0] is not None:  # Vérifier si l'élément est non nul
                list_lv2.append(lv2_row[0])
    conn.close()
    return list_lv2

def find_list_LV1(Data, promo_pair):
    conn = sqlite3.connect(Data)
    cursor = conn.cursor()
    list_lv1 = []
    for promo in promo_pair:
        cursor.execute("SELECT DISTINCT(LV1) FROM Student WHERE SCHOOL_YEAR = '" + promo + "';")
        lv1_results = cursor.fetchall()
        for lv1_row in lv1_results:
            if lv1_row[0] is not None:  # Vérifier si l'élément est non nul
                list_lv1.append(lv1_row[0])
    conn.close()
    return list_lv1

def find_list_lv(Data):
    conn = sqlite3.connect(Data)
    cursor = conn.cursor()
    list_lv = []
    cursor.execute("SELECT DISTINCT(LV1) FROM Student ;")
    lv_results = cursor.fetchall()
    for lv_row in lv_results:
        if lv_row[0] is not None:  # Vérifier si l'élément est non nul
            list_lv.append(lv_row[0])
    cursor.execute("SELECT DISTINCT(LV2) FROM Student ;")
    lv_results = cursor.fetchall()
    for lv_row in lv_results:
        if lv_row[0] is not None:  # Vérifier si l'élément est non nul
            list_lv.append(lv_row[0])
    conn.close()
    return list_lv

def get_all_students_from_a_pair_and_lv(Data, promo_pair, lv):
    conn = sqlite3.connect(Data)
    cursor = conn.cursor()
    group = []
    #print(promo_pair)
    grade = "GRADE_LV2"
    second_language = "2"
    if lv == "ANGLAIS":
        grade = "GRADE_LV1"
        second_language = "1"
    for promo in promo_pair:
        cursor.execute("SELECT EMAIL," + grade + ", SCHOOL_YEAR FROM Student WHERE SCHOOL_YEAR='" + promo + "'AND LV" + second_language + "='" + lv + "' ORDER BY GRADE_LV2 DESC;")
        group.extend(cursor.fetchall())
    group.sort(key=lambda x: x[1], reverse=True)    
    conn.close()
    return group

def get_all_students_from_a_pair_studying_this_lv(Data, promo_pair, language):
    conn = sqlite3.connect(Data)
    cursor = conn.cursor()
    if " " in language:
        language = language.split(' -')[0]  # Simplifie la langue en enlevant tout après ' -'
    total_count = 0
    second_language = "LV2"
    if language.upper() == "ANGLAIS":
        second_language = "LV1"
    
    for promo in promo_pair:
        #print(promo)
        cursor.execute(f"""
            SELECT COUNT(*)
            FROM Student
            WHERE SCHOOL_YEAR = ? AND {second_language} LIKE ?
            """, (promo, f"{language}%")) 
        total_count += cursor.fetchone()[0]
    
    conn.close()
    return total_count

def assigns_groups_to_students(Data, lv, id_course, group, teacher, slot):
    conn = sqlite3.connect(Data)
    cursor = conn.cursor()
    #print(lv, id_course, group, teacher, slot)
    cursor.execute("INSERT INTO Courses(LANGUAGE, ID_GROUP, ID_TEACHER, ID_AVAILABILITY) VALUES(?,?,?,?);", (lv, id_course, teacher, slot))
    for student in group:
        cursor.execute("INSERT INTO List_Groups_Students(ID_COURSE, ID_STUDENT) VALUES(?,?);", (id_course, student[0]))
    conn.commit()
    conn.close()

def get_students_count(Data, promo):
    conn = sqlite3.connect(Data)
    cursor = conn.cursor()
    cursor.execute("SELECT count(*) FROM Student WHERE SCHOOL_YEAR='" + promo + "';")
    return cursor.fetchone()[0]

def get_lv_slot(Data, promo_pair):
    """_summary_
    this function return all availabilties for a propmo
    Args:

    Returns:
        _type_: _description_
    """    
    conn = sqlite3.connect(Data)
    cursor = conn.cursor()
    slot_list = []
    for promo in promo_pair:
        cursor.execute("SELECT ID_Availability FROM Availability_Class WHERE ID_CLASS='" + promo + "';")
        slots = cursor.fetchall()
        for slot in slots:
            if slot not in slot_list:
                slot_list.append(slot)
        #print(slot_list)
    return list(set(slot_list))

def get_available_teacher(Data, slot, lv):
    conn = sqlite3.connect(Data)
    cursor = conn.cursor()
    teacher_availabilities = []
    if '-débutant' in lv:
        lv = lv.split(' -débutant')[0]
    for slo in slot:
        cursor.execute("""
                    SELECT Availability_Teachers.ID_Teacher, Availability_Teachers.ID_Availability 
                    FROM Availability_Teachers 
                    JOIN Teachers ON Availability_Teachers.ID_Teacher = Teachers.ID_teacher 
                    WHERE Availability_Teachers.ID_Availability = ? AND Teachers.subject = ? AND Availability_Teachers.ACTIVE = 1;
                    """
                    , (slo[0], lv))
        results = cursor.fetchall()
        #print(results)
        teacher_availabilities.extend(results)
        #print(teacher_availabilities)
    return teacher_availabilities

def get_nb_available_teacher(Data, slot, lv):
    conn = sqlite3.connect(Data)
    cursor = conn.cursor()
    nb_availabilities = 0
    if '-débutant' in lv:
        lv = lv.split(' -débutant')[0]
    for slo in slot:
        cursor.execute(
            """
            SELECT count(Availability_Teachers.ID_Teacher)
            FROM Availability_Teachers
            JOIN Teachers ON Availability_Teachers.ID_Teacher = Teachers.ID_teacher
            WHERE Availability_Teachers.ID_Availability = ? AND Teachers.subject = ? AND Availability_Teachers.ACTIVE = 0;
            """,
            (slo[0], lv)
        )
        nb = cursor.fetchall()
        nb_availabilities += nb[0][0]
    #print(nb_availabilities)
    return nb_availabilities

def get_available_teacher2(Data, slots, lv):
    conn = sqlite3.connect(Data)
    cursor = conn.cursor()
    teacher_availabilities = []
    if "COMPLEMENTAIRE" in lv or "DISPENSE" in lv :
        teacher_availabilities.append(('r', 'r'))    
    else : 
        for slot in slots:
            cursor.execute(
                """
                SELECT Availability_Teachers.ID_Teacher, Availability_Teachers.ID_Availability
                FROM Availability_Teachers
                JOIN Teachers ON Availability_Teachers.ID_Teacher = Teachers.ID_teacher
                WHERE Availability_Teachers.ID_Availability = ? AND Teachers.subject = ? AND Availability_Teachers.ACTIVE = 0
                ORDER BY Availability_Teachers.ID_Teacher AND Availability_Teachers.ID_Availability DESC;
                """,
                (slot[0], lv)
            )
            teacher_availabilities.extend(cursor.fetchall())
        teacher_availabilities.sort(key=lambda x: (x[0], x[1]))
    #print("aaaahhahahaa", teacher_availabilities)
    return teacher_availabilities

def get_available_room(Data, slots):
    conn = sqlite3.connect(Data)
    cursor = conn.cursor()
    rooms_available =[]
    cursor.execute("SELECT ID_room FROM Availability_Rooms WHERE ID_Availability like ?;", (slots))
    rooms_available.extend(cursor.fetchall())
    return rooms_available

