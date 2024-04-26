import sqlite3
# Fonction pour supprimer toutes les données d'une table donnée
def Delete_data_table(filename, table):
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



def insert_new_student(conn, student):
    cursor = conn.cursor()
    #SQL query to insert data
    #cursor.execute("")
    conn.commit()
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


def get_all_students_from_a_year_and_lv2(Data, year, lv2):
    conn = sqlite3.connect(Data)
    cursor = conn.cursor()
    cursor.execute("SELECT EMAIL FROM Student WHERE CLASS='" + year + "'AND LV2='" + lv2 + "';")
    group = cursor.fetchall()
    conn.commit()
    return group

def assigns_groups_to_students(Data, name_class, name_lv2, group_name, group):
    conn = sqlite3.connect(Data)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Groups(CLASS, LV, GROUP_LV) VALUES(?,?,?);", (name_class, name_lv2, group_name))
    for student in group:
        cursor.execute("UPDATE Student SET GROUP_LV2=? WHERE EMAIL=?;", (group_name, student))
        conn.commit()  
        conn.close()  