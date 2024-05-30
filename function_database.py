import sqlite3
# Fonction pour supprimer toutes les données d'une table donnée
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

def find_list_LV1(Data):
    conn = sqlite3.connect(Data)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT(LV1) FROM Student;")
    list_lv1 = cursor.fetchall()
    list_lv1 = [row[0] for row in list_lv1]
    conn.close()
    return list_lv1


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
    promo = "1a"
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Courses(LANGUAGE, ID_GROUP, ID_TEACHER, ID_AVAILIBITY) VALUES(?,?,?,?);", (lv, id_course, teacher, slot))
    for student in group:
        cursor.execute("INSERT INTO List_Groups_Students(ID_COURSE, ID_STUDENT) VALUES(?,?);", (id_course, student[0]))
    conn.commit()
    conn.close()

def get_students_count(Data, promo):
    conn = sqlite3.connect(Data)
    cursor = conn.cursor()
    cursor.execute("SELECT count(*) FROM Student WHERE SCHOOL_YEAR='" + promo + "';")
    return cursor.fetchone()[0]

def get_lv_slot_count(Data, promo_pair):
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
        slot_list.extend(cursor.fetchall())
        #print(slot_list)
    return list(set(slot_list))


def get_available_teacher(Data, slot, lv):
    """
    this function return all the teacher available for the slot in entry.

    Args:
        Data (_type_): _description_
        slot (_type_): _description_

    Returns:
        _type_: _description_
    """    
    conn = sqlite3.connect(Data)
    cursor = conn.cursor()
    teacher_availabilities = []
    slot_nbr_for_lv = 0
    #print(lv)
    if ' -débutant' in lv:
        lv = lv.split(' -débutant')[0]
    for slo in slot:
        cursor.execute(
            """
            SELECT Availability_Teachers.ID_Teacher, Availability_Teachers.ID_Availability
            FROM Availability_Teachers
            JOIN Teachers ON Availability_Teachers.ID_Teacher = Teachers.ID_teacher
            WHERE Availability_Teachers.ID_Availability = ? AND Teachers.subject = ?;
            """,
            (slo[0], lv)
        )
        teacher_availabilities.extend(cursor.fetchall())
        #print(teacher_availabilities)
    return teacher_availabilities
