import sqlite3
import re
import random

def get_number_conflict_per_group(Data):
    conn = sqlite3.connect(Data)  # Connect to the SQLite database
    cursor = conn.cursor()  # Create a cursor object to execute SQL commands
    
    # SQL query to get students and their courses along with the course availability
    query = """
        SELECT 
            c1.ID_COURSE,
            COALESCE(conflict_data.number_of_conflicts, 0) AS number_of_conflicts
        FROM 
            Courses c1
        LEFT JOIN (
            SELECT 
                c1.ID_COURSE,
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
                c1.LANGUAGE = 'ANG'
                AND c1.ID_AVAILABILITY = c2.ID_AVAILABILITY
                AND c1.ID_COURSE != c2.ID_COURSE
            GROUP BY 
                c1.ID_COURSE
        ) AS conflict_data ON c1.ID_COURSE = conflict_data.ID_COURSE
        WHERE 
            c1.LANGUAGE = 'ANG';
    """
    cursor.execute(query)
    group_conflict = cursor.fetchall() # Fetch all results
    conn.close()
    # Function to extract the numeric part of the course ID
    def extract_number(course_id):
        match = re.search(r'G(\d+)', course_id)
        return int(match.group(1)) if match else float('inf')

    # Sort the conflicts data using the extracted number as the key
    sorted_conflicts = sorted(group_conflict, key=lambda x: extract_number(x[0]))
    return sorted_conflicts

def get_students_in_conflict(course_id, db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    query_students = """
        SELECT DISTINCT lgs1.ID_STUDENT
        FROM List_Groups_Students lgs1
        JOIN Courses c1 ON lgs1.ID_COURSE = c1.ID_COURSE
        JOIN List_Groups_Students lgs2 ON lgs1.ID_STUDENT = lgs2.ID_STUDENT
        JOIN Courses c2 ON lgs2.ID_COURSE = c2.ID_COURSE
        WHERE c1.ID_COURSE = ?
        AND c1.ID_AVAILABILITY = c2.ID_AVAILABILITY
        AND c1.ID_COURSE != c2.ID_COURSE;
    """
    cursor.execute(query_students, (course_id,))
    student_ids = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    return student_ids

# Exemple de fonction pour mettre à jour le groupe d'un étudiant
def update_student_group(student_id, new_course_id, db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    update_query = """
        UPDATE List_Groups_Students
        SET ID_COURSE = ?
        WHERE ID_STUDENT = ?
        AND ID_COURSE IN (
            SELECT ID_COURSE 
            FROM Courses 
            WHERE LANGUAGE = 'ANG'
        );
    """
    cursor.execute(update_query, (new_course_id, student_id))
    conn.commit()
    
    conn.close()
    
    
def exchange_students(conflicts_data, db_path):
    for i in range(len(conflicts_data)):
        current_course_id, current_conflicts = conflicts_data[i]
        students_in_conflict = get_students_in_conflict(current_course_id, db_path)
        # Try to resolve conflicts with the previous group if possible
        if i > 0:
            prev_course_id, prev_conflicts = conflicts_data[i - 1]
            prev_students_in_conflict = get_students_in_conflict(prev_course_id, db_path)
            for student_id in students_in_conflict[:]:  # Copy the list to avoid modification during iteration
                if len(prev_students_in_conflict) != 0 and current_conflicts != 0:
                    prev_student_id = random.choice(prev_students_in_conflict)
                    update_student_group(prev_student_id, current_course_id, db_path)
                    update_student_group(student_id, prev_course_id, db_path)
                    current_conflicts -= 1
                    prev_conflicts -= 1
                    prev_students_in_conflict.remove(prev_student_id)
                    students_in_conflict.remove(student_id)
            conflicts_data[i - 1] = (prev_course_id, prev_conflicts)

        # Update the conflicts data for the current group
        conflicts_data[i] = (current_course_id, current_conflicts)

        # Try to resolve conflicts with the next group if possible
        if i < len(conflicts_data) - 2:
            next_course_id, next_conflicts = conflicts_data[i + 1]
            next_students_in_conflict = get_students_in_conflict(next_course_id, db_path)
            for student_id in students_in_conflict[:]:  # Copy the list to avoid modification during iteration
                if len(next_students_in_conflict) != 0 and current_conflicts != 0:
                    next_student_id = random.choice(next_students_in_conflict)
                    current_conflicts -= 1
                    next_conflicts -= 1
                    students_in_conflict.remove(student_id)
                    next_students_in_conflict.remove(next_student_id)
            conflicts_data[i + 1] = (next_course_id, next_conflicts)
        # Update the conflicts data for the current group
        conflicts_data[i] = (current_course_id, current_conflicts)


def get_available_students(course_id, slot_current_course, db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    query_available_students = """
        SELECT DISTINCT lgs1.ID_STUDENT
        FROM List_Groups_Students lgs1
        JOIN Courses c1 ON lgs1.ID_COURSE = c1.ID_COURSE
        WHERE c1.ID_COURSE = ?
        AND lgs1.ID_STUDENT NOT IN (
            SELECT lgs2.ID_STUDENT
            FROM List_Groups_Students lgs2
            JOIN Courses c2 ON lgs2.ID_COURSE = c2.ID_COURSE
            WHERE c2.ID_AVAILABILITY = ?
        );
    """
    cursor.execute(query_available_students, (course_id, slot_current_course))
    available_students = [row[0] for row in cursor.fetchall()]

    conn.close()
    return available_students

def get_slot_course(db_path, course_id):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    query_slot = """
        SELECT ID_AVAILABILITY
        FROM Courses
        WHERE ID_COURSE = ?;
    """
    cursor.execute(query_slot, (course_id,))
    slot = cursor.fetchone()

    conn.close()
    return slot[0] if slot else None

def exchange_students_with_different_schedule(conflicts_data, db_path):
    for i in range(len(conflicts_data)):
        current_course_id, current_conflicts = conflicts_data[i]
        students_in_conflict = get_students_in_conflict(current_course_id, db_path)
        slot_current_course = get_slot_course(db_path, current_course_id)
        
        # Try to resolve conflicts with the previous group if possible
        if i > 2:
            prev_course_id, prev_conflicts = conflicts_data[i - 1]
            available_students = get_available_students(prev_course_id, slot_current_course, db_path)
            for student_id in students_in_conflict[:]:  # Copy the list to avoid modification during iteration
                if len(available_students) != 0 and current_conflicts != 0:
                    available_student_id = random.choice(available_students)
                    update_student_group(available_student_id, current_course_id, db_path)
                    update_student_group(student_id, prev_course_id, db_path)
                    current_conflicts -= 1
                    available_students.remove(available_student_id)
                    students_in_conflict.remove(student_id)
            conflicts_data[i - 1] = (prev_course_id, prev_conflicts)

        # Update the conflicts data for the current group
        conflicts_data[i] = (current_course_id, current_conflicts)

        # Try to resolve conflicts with the next group if possible
        if i < len(conflicts_data) - 2:
            next_course_id, next_conflicts = conflicts_data[i + 1]
            available_students = get_available_students(next_course_id, slot_current_course, db_path)
            for student_id in students_in_conflict[:]:  # Copy the list to avoid modification during iteration
                if len(available_students) != 0 and current_conflicts != 0:
                    available_student_id = random.choice(available_students)
                    update_student_group(available_student_id, current_course_id, db_path)
                    update_student_group(student_id, next_course_id, db_path)
                    current_conflicts -= 1
                    available_students.remove(available_student_id)
                    students_in_conflict.remove(student_id)
            conflicts_data[i + 1] = (next_course_id, next_conflicts)
        # Update the conflicts data for the current group
        conflicts_data[i] = (current_course_id, current_conflicts)

def resolve_conflict(Data):
    conflict = get_number_conflict_per_group(Data)
    exchange_students(conflict, Data)
    conflict = get_number_conflict_per_group(Data)
    exchange_students_with_different_schedule(conflict, Data)
