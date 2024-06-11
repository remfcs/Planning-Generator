####################################################################################
#                          Conflict Resolution Functions                           #
####################################################################################
# Provides functionalities to detect and resolve scheduling conflicts for students #
# enrolled in 2 courses simultaneously. It includes detecting conflicts, updating  #
# student groups, and resolving conflicts by exchanging students between groups.   #
####################################################################################

# --------------------------------------------------------------------------------
# Modules:
# --------------------------------------------------------------------------------
# 1. get_number_conflict_per_group:
#    - Retrieves the number of conflicts for each course group.
#
# 2. get_students_in_conflict:
#    - Retrieves the list of students who have scheduling conflicts for a given course.
#
# 3. update_student_group:
#    - Updates the course group of a student.
#
# 4. exchange_students:
#    - Exchanges students between groups to resolve scheduling conflicts.
#
# 5. get_available_students:
#    - Retrieves the list of students available for a different schedule.
#
# 6. get_slot_course:
#    - Retrieves the availability slot for a given course.
#
# 7. exchange_students_with_different_schedule:
#    - Exchanges students between groups with different schedules to resolve conflicts.
#
# 8. resolve_conflict:
#    - Main function to detect and resolve scheduling conflicts.
# --------------------------------------------------------------------------------

# --------------------------------------------------------------------------------
# Dependencies:
# --------------------------------------------------------------------------------
# - sqlite3
# - re
# - random
# --------------------------------------------------------------------------------

import sqlite3
import re
import random

def get_number_conflict_per_group(Data):
    """
    Retrieves the number of conflicts for each course group.

    Args:
        Data (str): Path to the SQLite database.

    Returns:
        list: Sorted list of tuples containing course IDs and their number of conflicts.
    """
    conn = sqlite3.connect(Data)
    cursor = conn.cursor()

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
    group_conflict = cursor.fetchall()
    conn.close()

    def extract_number(course_id):
        match = re.search(r'G(\d+)', course_id)
        return int(match.group(1)) if match else float('inf')

    sorted_conflicts = sorted(group_conflict, key=lambda x: extract_number(x[0]))
    return sorted_conflicts

def get_students_in_conflict(course_id, db_path):
    """
    Retrieves the list of students who have scheduling conflicts for a given course.

    Args:
        course_id (str): The course ID to check for conflicts.
        db_path (str): Path to the SQLite database.

    Returns:
        list: List of student IDs in conflict.
    """
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

def update_student_group(student_id, new_course_id, db_path):
    """
    Updates the course group of a student.

    Args:
        student_id (str): The student ID to be updated.
        new_course_id (str): The new course ID to assign to the student.
        db_path (str): Path to the SQLite database.
    """
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
    """
    Exchanges students between groups to resolve scheduling conflicts.

    Args:
        conflicts_data (list): List of tuples containing course IDs and their number of conflicts.
        db_path (str): Path to the SQLite database.
    """
    conflicts_data_dict = {conflict[0]: conflict[1] for conflict in conflicts_data}

    for i in range(len(conflicts_data)):
        
        promo_in_conflict = conflicts_data[i][0].split("_")[1]
        language = conflicts_data[i][0].split("_")[2]
        group_in_conflict = conflicts_data[i][0].split("_")[0]
        number_group = int(group_in_conflict[1])
        current_course_id, current_conflicts = conflicts_data[i]
        current_conflicts = len(get_students_in_conflict(current_course_id, db_path))
        students_in_conflict = get_students_in_conflict(current_course_id, db_path)
        prev_course_id = "G"+str(number_group-1)+"_"+promo_in_conflict+"_"+language
        next_course_id = "G"+str(number_group+1)+"_"+promo_in_conflict+"_"+language
        # Try to resolve conflicts with the previous group if possible
        if prev_course_id in conflicts_data_dict:
            prev_conflicts = conflicts_data_dict[prev_course_id]
            prev_students_in_conflict = get_students_in_conflict(prev_course_id, db_path)
            for student_id in students_in_conflict[:]:
                if len(prev_students_in_conflict) != 0 and current_conflicts != 0:
                    prev_student_id = random.choice(prev_students_in_conflict)
                    update_student_group(prev_student_id, current_course_id, db_path)
                    update_student_group(student_id, prev_course_id, db_path)
                    current_conflicts -= 1
                    prev_conflicts -= 1
                    prev_students_in_conflict.remove(prev_student_id)
                    students_in_conflict.remove(student_id)
        conflicts_data[i] = (current_course_id, current_conflicts)

        # Try to resolve conflicts with the next group if possible
        if next_course_id in conflicts_data_dict:
            next_conflicts = conflicts_data_dict[next_course_id]
            next_students_in_conflict = get_students_in_conflict(next_course_id, db_path)
            for student_id in students_in_conflict[:]:
                if len(next_students_in_conflict) != 0 and current_conflicts != 0:
                    next_student_id = random.choice(next_students_in_conflict)
                    update_student_group(next_student_id, current_course_id, db_path)
                    update_student_group(student_id, next_course_id, db_path)
                    current_conflicts -= 1
                    next_conflicts -= 1
                    next_students_in_conflict.remove(next_student_id)
                    students_in_conflict.remove(student_id)
        conflicts_data[i] = (current_course_id, current_conflicts)

def get_available_students(course_id, slot_current_course, db_path):
    """
    Retrieves the list of students available for a different schedule.

    Args:
        course_id (str): The course ID to check availability for.
        slot_current_course (str): The time slot of the current course.
        db_path (str): Path to the SQLite database.

    Returns:
        list: List of available student IDs.
    """
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
    """
    Retrieves the availability slot for a given course.

    Args:
        db_path (str): Path to the SQLite database.
        course_id (str): The course ID to retrieve the slot for.

    Returns:
        str: The availability slot of the course.
    """
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
    """
    Exchanges students between groups with different schedules to resolve conflicts.

    Args:
        conflicts_data (list): List of tuples containing course IDs and their number of conflicts.
        db_path (str): Path to the SQLite database.
    """
    conflicts_data_dict = {conflict[0]: conflict[1] for conflict in conflicts_data}
    for i in range(len(conflicts_data)):
        promo_in_conflict = conflicts_data[i][0].split("_")[1]
        language = conflicts_data[i][0].split("_")[2]
        group_in_conflict = conflicts_data[i][0].split("_")[0]
        number_group = int(group_in_conflict[1])
        current_course_id, current_conflicts = conflicts_data[i]
        slot_current_course = get_slot_course(db_path, current_course_id)
        j=1
        while len(get_students_in_conflict(current_course_id, db_path)) != 0 and j < 5:
            prev_course_id = "G"+str(number_group-j)+"_"+promo_in_conflict+"_"+language
            next_course_id = "G"+str(number_group+j)+"_"+promo_in_conflict+"_"+language
            students_in_conflict = get_students_in_conflict(current_course_id, db_path)
            #print(prev_course_id , current_course_id, next_course_id)
            # Try to resolve conflicts with the previous group if possible
            if prev_course_id in conflicts_data_dict:
                available_students = get_available_students(prev_course_id, slot_current_course, db_path)
                for student_id in students_in_conflict[:]:
                    if len(available_students) != 0 and current_conflicts != 0:
                        available_student_id = random.choice(available_students)
                        update_student_group(available_student_id, current_course_id, db_path)
                        update_student_group(student_id, prev_course_id, db_path)
                        current_conflicts -= 1
                        available_students.remove(available_student_id)
                        students_in_conflict.remove(student_id)
            conflicts_data[i] = (current_course_id, current_conflicts)

            # Try to resolve conflicts with the next group if possible
            if next_course_id in conflicts_data_dict:
                available_students = get_available_students(next_course_id, slot_current_course, db_path)
                for student_id in students_in_conflict[:]:
                    if len(available_students) != 0 and current_conflicts != 0:
                        available_student_id = random.choice(available_students)
                        update_student_group(available_student_id, current_course_id, db_path)
                        update_student_group(student_id, next_course_id, db_path)
                        current_conflicts -= 1
                        available_students.remove(available_student_id)
                        students_in_conflict.remove(student_id)
            conflicts_data[i] = (current_course_id, current_conflicts)
            j+=1
            

def resolve_conflict(Data):
    """
    Main function to detect and resolve scheduling conflicts.

    Args:
        Data (str): Path to the SQLite database.
    """
    conflict = get_number_conflict_per_group(Data)
    exchange_students(conflict, Data)
    conflict = get_number_conflict_per_group(Data)
    exchange_students_with_different_schedule(conflict, Data)