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
    
    
def find_list_CLASS(Data):
    conn = sqlite3.connect(Data)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT(CLASS) FROM Student;")
    list_Class = cursor.fetchall()
    list_Class = [row[0] for row in list_Class]
    conn.close()
    return list_Class

def find_list_LV2(Data, Class):
    conn = sqlite3.connect(Data)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT(LV2) FROM Student WHERE Class = '" + Class + "';")
    list_lv2 = cursor.fetchall()
    list_lv2 = [row[0] for row in list_lv2]
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


def get_all_students_from_a_year_and_lv2(Data, promo, lv2):
    conn = sqlite3.connect(Data)
    cursor = conn.cursor()
    cursor.execute("SELECT EMAIL, GRADE_LV2 FROM Student WHERE CLASS='" + promo + "'AND LV2='" + lv2 + "' ORDER BY GRADE_LV2 DESC;")
    group = cursor.fetchall()
    conn.commit()
    return group

def assigns_groups_to_students(Data, name_class, name_lv2, group_name, group):
    conn = sqlite3.connect(Data)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Groups(CLASS, LV, GROUP_LV) VALUES(?,?,?);", (name_class, name_lv2, group_name))
    for student in group:
        cursor.execute("UPDATE Student SET GROUP_LV2=? WHERE EMAIL=?;", (group_name, student[0]))
    conn.commit()  
    conn.close()  

def get_students_count(Data, promo):
    conn = sqlite3.connect(Data)
    cursor = conn.cursor()
    cursor.execute("SELECT count(*) FROM Student WHERE CLASS='" + promo + "';")
    return cursor.fetchone()[0]


    