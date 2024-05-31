import sqlite3
import function_create_groups
import function_read_folder 
import function_database
import function_file_db


Data = 'data/test.sqlite3'



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
            Courses c1 ON lgs1.ID_COURSE = c1.ID_GROUP
        JOIN 
            List_Groups_Students lgs2 ON lgs1.ID_STUDENT = lgs2.ID_STUDENT
        JOIN 
            Courses c2 ON lgs2.ID_COURSE = c2.ID_GROUP
        WHERE 
            c1.ID_AVAILABILITY = c2.ID_AVAILABILITY
            AND c1.ID_GROUP != c2.ID_GROUP
            AND c1.ID_GROUP < c2.ID_GROUP
        ORDER BY 
            lgs1.ID_STUDENT, c1.ID_AVAILABILITY;
            """
    cursor.execute(query)
    conflicts = cursor.fetchall()
    conn.close()
    return conflicts



def get_list_group(Data, language):
    conn = sqlite3.connect(Data)
    cursor = conn.cursor()
    cursor.execute("SELECT ID_GROUP FROM Courses where LANGUAGE = ?;", (language,))
    result = cursor.fetchall()
    conn.close()
    return result 




conflicts = get_students_with_schedule_conflicts(Data)
print("Étudiants avec des conflits d'horaires :", len(conflicts))
#print(conflicts)
for conflict in conflicts:
    print(conflict)

def resolution_conflict(data):
    conflicts = get_students_with_schedule_conflicts(Data)
    for conflict in conflicts:
        return
    return