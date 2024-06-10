import sqlite3
from algo_feature import function_conflict
import random 


def get_number_of_students_per_group(db_path):
    conn = sqlite3.connect(db_path)  # Connect to the SQLite database
    cursor = conn.cursor()  # Create a cursor object to execute SQL commands

    # SQL query to get the number of students per group
    query = """
        SELECT 
            c.ID_COURSE,
            COUNT(lgs.ID_STUDENT) AS number_of_students
        FROM 
            Courses c
        LEFT JOIN 
            List_Groups_Students lgs ON c.ID_COURSE = lgs.ID_COURSE
        WHERE 
            c.LANGUAGE = 'ANG'
        GROUP BY 
            c.ID_COURSE
        ORDER BY 
            c.ID_COURSE;
    """
    
    cursor.execute(query)
    group_student_counts = cursor.fetchall()
    
    conn.close()

    # Print the number of students in each group
    for course_id, number_of_students in group_student_counts:
        print(f'Course ID: {course_id}, Number of Students: {number_of_students}')
        
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


#print(get_average(data_path))







def check_course_conflicts(course_id, db_path='your_database.db'):
    # Connexion à la base de données
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Requête SQL pour compter les conflits pour un cours donné
    query = """
    SELECT 
        COUNT(DISTINCT lgs1.ID_STUDENT) AS number_of_conflicts
    FROM 
        List_Groups_Students lgs1
    JOIN 
        Courses c1 ON lgs1.ID_COURSE = c1.ID_COURSE
    JOIN 
        List_Groups_Students lgs2 ON lgs1.ID_STUDENT = lgs2.ID_STUDENT
    JOIN 
        Courses c2 ON lgs2.ID_COURSE = c2.ID_COURSE
    WHERE 
        c1.ID_COURSE = ?
        AND c1.ID_AVAILABILITY = c2.ID_AVAILABILITY
        AND c1.ID_COURSE != c2.ID_COURSE;
    """

    # Exécution de la requête
    cursor.execute(query, (course_id,))
    print(cursor.fetchone())

    # Fermeture de la connexion à la base de données
    conn.close()

Data = "data/database.sqlite3"
conflict = function_conflict.get_number_conflict_per_group(Data)
print(conflict)
        

get_number_of_students_per_group(Data)
get_number_of_students_per_group(Data)
