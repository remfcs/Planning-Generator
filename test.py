import sqlite3
import function_create_groups
import function_read_folder 
import function_database
import function_file_db
import function_conflict


Data = 'data/test.sqlite3'

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


print(get_nb_student_by_group(Data))
