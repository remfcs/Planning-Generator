import sqlite3
import pandas as pd

def get_students_with_schedule_conflicts(data_path):
    conn = sqlite3.connect(data_path)
    cursor = conn.cursor()

    # Get students and their courses along with the course availability
    query = """
    SELECT s.EMAIL, c1.ID_AVAILIBITY AS AVAILABILITY_ENGLISH, c2.ID_AVAILIBITY AS AVAILABILITY_LV2
    FROM Student s
    JOIN List_Groups_Students lgs1 ON s.EMAIL = lgs1.ID_STUDENT
    JOIN Courses c1 ON lgs1.ID_COURSE = c1.ID_COURSE
    JOIN List_Groups_Students lgs2 ON s.EMAIL = lgs2.ID_STUDENT
    JOIN Courses c2 ON lgs2.ID_COURSE = c2.ID_COURSE
    WHERE c1.ID_AVAILIBITY = c2.ID_AVAILIBITY
    AND c1.ID_GROUP = 'ANGLAIS'
    AND c2.ID_GROUP != 'ANGLAIS';
    """

    cursor.execute(query)
    conflicts = cursor.fetchall()
    conn.close()

    return conflicts
data_path = 'data/test.sqlite3'
# conflicts = get_students_with_schedule_conflicts(data_path)
# print("Étudiants avec des conflits d'horaires :")
# for conflict in conflicts:
#     print(conflict)
    
    


def get_course_details_with_conflicts(data_path):
    conn = sqlite3.connect(data_path)
    cursor = conn.cursor()

    # Query to get all course details with student count and professor info
    query = """
    SELECT
        c.ID_COURSE,
        c.ID_GROUP,
        COUNT(lgs.ID_STUDENT) AS STUDENT_COUNT,
        (SELECT COUNT(*)
         FROM List_Groups_Students lgs2
         JOIN Courses c2 ON lgs2.ID_COURSE = c2.ID_COURSE
         WHERE lgs2.ID_STUDENT IN (
             SELECT lgs3.ID_STUDENT
             FROM List_Groups_Students lgs3
             WHERE lgs3.ID_COURSE = c.ID_COURSE
         )
         AND c2.ID_AVAILIBITY = c.ID_AVAILIBITY
         AND c2.ID_COURSE != c.ID_COURSE
        ) AS CONFLICT_COUNT,
        c.ID_TEACHER,
        c.ID_AVAILIBITY AS TIME_SLOT
    FROM
        Courses c
    JOIN List_Groups_Students lgs ON c.ID_COURSE = lgs.ID_COURSE
    GROUP BY
        c.ID_TEACHER, c.ID_GROUP, c.ID_COURSE, c.ID_AVAILIBITY
    """

    # Execute the query and fetch results
    cursor.execute(query)
    result = cursor.fetchall()

    # Convert results to a pandas DataFrame for better readability
    columns = ['ID_COURSE', 'ID_GROUP', 'STUDENT_COUNT', 'CONFLICT_COUNT', 'PROFESSOR', 'TIME_SLOT']
    course_details_df = pd.DataFrame(result, columns=columns)

    conn.close()

    return course_details_df

course_details_df = get_course_details_with_conflicts(data_path)
print(course_details_df)