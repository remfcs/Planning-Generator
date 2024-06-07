import sqlite3

def get_students_with_grades_in_groups(data_path):
    conn = sqlite3.connect(data_path)
    cursor = conn.cursor()

    # Exécute la requête SQL
    cursor.execute("""
        SELECT 
            List_Groups_Students.ID_Course,  
            Student.EMAIL,
            Student.NAME,
            Student.SURNAME,
            Student.GRADE_LV2
        FROM 
            List_Groups_Students
        JOIN 
            Student ON List_Groups_Students.ID_Student = Student.EMAIL
    """)

    # Récupère les résultats
    results = cursor.fetchall()

    # Ferme la connexion à la base de données
    conn.close()

    return results

def find_outliers(data_path, threshold):
    conn = sqlite3.connect(data_path)
    cursor = conn.cursor()

    # Calcul de la moyenne des notes par groupe
    cursor.execute("""
        SELECT 
            List_Groups_Students.ID_Course,
            AVG(Student.GRADE_LV2) AS Average_Grade
        FROM 
            List_Groups_Students
        JOIN 
            Student ON List_Groups_Students.ID_Student = Student.EMAIL
        GROUP BY 
            List_Groups_Students.ID_Course
    """)
    group_avg_dict = dict(cursor.fetchall())

    # Récupération des notes des étudiants
    cursor.execute("""
        SELECT 
            List_Groups_Students.ID_Course,
            List_Groups_Students.ID_Student,
            Student.NAME,
            Student.SURNAME,
            Student.GRADE_LV2
        FROM 
            List_Groups_Students
        JOIN 
            Student ON List_Groups_Students.ID_Student = Student.EMAIL
    """)
    student_grades = cursor.fetchall()

    # Recherche des outliers
    outliers = []
    for group_id, student_id, name, surname, grade in student_grades:
        group_avg = group_avg_dict.get(group_id)
        if group_avg is not None:
            if abs(grade - group_avg) >= threshold:
                outliers.append((group_id, student_id, name, surname, grade, group_avg))

    # Fermeture de la connexion à la base de données
    conn.close()

    return outliers

data_path = "data/test.sqlite3"
outliers = find_outliers(data_path, 1.5)
print("*"*50)
for row in outliers:
    if not 'ANG' in row[0]:
        print(row)
print("*"*50)
def get_average(data_path):
    conn = sqlite3.connect(data_path)
    cursor = conn.cursor()

    # Exécute la requête SQL
    cursor.execute("""
        SELECT 
            List_Groups_Students.ID_Course,
            AVG(Student.GRADE_LV2) AS Average_Grade
        FROM 
            List_Groups_Students
        JOIN 
            Student ON List_Groups_Students.ID_Student = Student.Email
        GROUP BY 
            List_Groups_Students.ID_Course
    """)

    # Récupère les résultats
    results = cursor.fetchall()

    # Ferme la connexion à la base de données
    conn.close()

    return results

# Exemple d'utilisation
data_path = "data/test.sqlite3"
students_with_grades_in_groups = get_students_with_grades_in_groups(data_path)
for row in students_with_grades_in_groups:
    print(row)

print(get_average(data_path))




