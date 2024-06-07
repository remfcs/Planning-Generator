import sqlite3
import re


def get_students_with_schedule_conflicts(Data):
    """
    Retrieves students with schedule conflicts from the database.

    Parameters:
    Data (str): Path to the SQLite database file.

    Returns:
    list: Processed conflicts sorted by availability and course group number.
    """
    conn = sqlite3.connect(Data)  # Connect to the SQLite database
    cursor = conn.cursor()  # Create a cursor object to execute SQL commands
    
    # SQL query to get students and their courses along with the course availability
    query = """
        SELECT 
            lgs1.ID_STUDENT,
            c1.ID_AVAILABILITY,
            c1.ID_GROUP AS COURSE_1,
            c2.ID_GROUP AS COURSE_2
        FROM 
            List_Groups_Students lgs1
        JOIN 
            (SELECT ID_GROUP, ID_AVAILABILITY FROM Courses ORDER BY LENGTH(ID_GROUP), ID_GROUP) AS c1 
            ON lgs1.ID_COURSE = c1.ID_GROUP
        JOIN 
            List_Groups_Students lgs2 ON lgs1.ID_STUDENT = lgs2.ID_STUDENT
        JOIN 
            Courses c2 ON lgs2.ID_COURSE = c2.ID_GROUP
        WHERE 
            c1.ID_AVAILABILITY = c2.ID_AVAILABILITY
            AND c1.ID_GROUP != c2.ID_GROUP
            AND c1.ID_GROUP < c2.ID_GROUP
        ORDER BY 
            c1.ID_AVAILABILITY, LENGTH(c1.ID_GROUP), c1.ID_GROUP;
    """
    cursor.execute(query)  # Execute the SQL query
    conflicts = cursor.fetchall()  # Fetch all results
    conn.close()  # Close the database connection
    
    processed_conflicts = []
    for conflict in conflicts:
        student_id, availability, course_1, course_2 = conflict
        # Process conflicts to ensure the English course (if present) is the first in the tuple
        if course_1.endswith('_ANG'):
            processed_conflicts.append((student_id, availability, course_1, course_2))
        elif course_2.endswith('_ANG'):
            processed_conflicts.append((student_id, availability, course_2, course_1))
        else:
            processed_conflicts.append((student_id, availability, course_1, course_2))
 
    # Function to sort conflicts by availability and course number
    def sort_key(x):
        availability, course_1, _ = x[1:4]
        match = re.search(r'G(\d+)_', course_1)
        course_num = int(match.group(1)) if match else float('inf')
        return (availability, course_num, course_1)

    processed_conflicts.sort(key=sort_key)  # Sort conflicts using the sort_key function
    return processed_conflicts  # Return the sorted conflicts

def get_list_group(Data, language, promo_list):
    """
    Retrieves the number of groups that match the given language and promo list.

    Parameters:
    Data (str): Path to the SQLite database file.
    language (str): Language of the course.
    promo_list (list): List of promo codes.

    Returns:
    int: Number of matching groups.
    """
    conn = sqlite3.connect(Data)  # Connect to the SQLite database
    cursor = conn.cursor()  # Create a cursor object to execute SQL commands
    result_str = '%' + ', '.join(promo_list) + '%'  # Format the promo list for the SQL query
    cursor.execute("SELECT ID_GROUP FROM Courses WHERE LANGUAGE LIKE ? AND ID_GROUP like ?;", (language, result_str,))
    result = cursor.fetchall()  # Fetch all results
    conn.close()  # Close the database connection
    return len(result)  # Return the number of matching groups

def get_promo_list(Data, id_availability, id_group):
    """
    Retrieves the promo list for a given availability and group ID.

    Parameters:
    Data (str): Path to the SQLite database file.
    id_availability (str): Availability ID.
    id_group (str): Group ID.

    Returns:
    str: Promo list.
    """
    conn = sqlite3.connect(Data)  # Connect to the SQLite database
    cursor = conn.cursor()  # Create a cursor object to execute SQL commands
    cursor.execute("SELECT PROMO FROM Courses WHERE ID_GROUP LIKE ? AND ID_AVAILABILITY LIKE ?;", (id_group, id_availability,))
    result = cursor.fetchall()  # Fetch all results
    conn.close()  # Close the database connection
    return result[0][0]  # Return the promo list

def resolution_conflict(Data):
    """
    Resolves schedule conflicts by assigning students to new groups.

    Parameters:
    Data (str): Path to the SQLite database file.
    """
    conflicts = get_students_with_schedule_conflicts(Data)  # Get students with schedule conflicts
    for conflict in conflicts:
        new_group = get_new_group(Data, conflict[2])  # Get a new group for the conflicting course
        conn = sqlite3.connect(Data)  # Connect to the SQLite database
        cursor = conn.cursor()  # Create a cursor object to execute SQL commands
        cursor.execute("UPDATE List_Groups_Students SET ID_COURSE = ? WHERE ID_STUDENT LIKE ? AND ID_COURSE LIKE ?;", 
                       (new_group, conflict[0], conflict[2]))
        conn.commit()  # Commit the transaction
        conn.close()  # Close the database connection
    return

#print(resolution_conflict('data/test.sqlite3'))

def get_nb_student_by_group(Data):
    """
    Retrieves the number of students in each group that ends with '_ANG'.

    Parameters:
    Data (str): Path to the SQLite database file.

    Returns:
    list: Number of students in each group.
    """
    conn = sqlite3.connect(Data)  # Connect to the SQLite database
    cursor = conn.cursor()  # Create a cursor object to execute SQL commands
    query = """
        SELECT lst.ID_COURSE, COUNT(lst.ID_STUDENT)
        FROM List_Groups_Students AS lst
        WHERE lst.ID_COURSE LIKE '%ANG'
        GROUP BY lst.ID_COURSE
        ORDER BY LENGTH(lst.ID_COURSE), lst.ID_COURSE;
    """
    cursor.execute(query)  # Execute the SQL query
    result = cursor.fetchall()  # Fetch all results
    conn.close()  # Close the database connection
    return result  # Return the number of students in each group

def get_list_stutents_from_group(Data, id_group):
    """
    Retrieves the list of students from a specific group.

    Parameters:
    Data (str): Path to the SQLite database file.
    id_group (str): Group ID.

    Returns:
    list: List of students in the group.
    """
    conn = sqlite3.connect(Data)  # Connect to the SQLite database
    cursor = conn.cursor()  # Create a cursor object to execute SQL commands
    query = """
        SELECT ID_STUDENT FROM List_Groups_Students WHERE ID_COURSE LIKE ? ORDER BY RANDOM();
    """
    cursor.execute(query, (id_group,))  # Execute the SQL query with the group ID
    result = cursor.fetchall()  # Fetch all results
    conn.close()  # Close the database connection
    return result  # Return the list of students

def get_new_group(Data, id_group):
    """
    Determines a new group for a given group ID.

    Parameters:
    Data (str): Path to the SQLite database file.
    id_group (str): Group ID.

    Returns:
    str: New group ID.
    """
    match = re.search(r'G(\d+)_', id_group)  # Match the group number in the ID
    after_underscore = id_group[id_group.index('_'):]  # Get the substring after the underscore
    promo_list = id_group.split('_')[1]  # Get the promo list from the group ID
    language = id_group.split('_')[2]  # Get the language from the group ID
    
    if match:
        value_between_G_and_underscore = match.group(1)  # Extract the group number
    
    # Determine the new group based on the current group number
    if int(value_between_G_and_underscore) % 2 == 0:
        if int(value_between_G_and_underscore) == get_list_group(Data, language, promo_list):
            new_group = "G" + str(int(value_between_G_and_underscore) + 1) + after_underscore
        else:
            new_group = "G" + str(int(value_between_G_and_underscore) - 1) + after_underscore
    elif int(value_between_G_and_underscore) % 2 == 1:
        if int(value_between_G_and_underscore) == get_list_group(Data, language, promo_list):
            new_group = "G" + str(int(value_between_G_and_underscore) - 1) + after_underscore
        else:
            new_group = "G" + str(int(value_between_G_and_underscore) + 1) + after_underscore
    
    return new_group  # Return the new group ID

def balance_groups(Data, max_by_class):
    """
    Balances the number of students in each group to ensure no group exceeds the maximum size.

    Parameters:
    Data (str): Path to the SQLite database file.
    max_by_class (int): Maximum number of students per group.
    """
    list_groups = get_nb_student_by_group(Data)  # Get the number of students in each group
    for group in list_groups:
        if group[1] > max_by_class:  # Check if the group exceeds the maximum size
            n = group[1] - max_by_class  # Calculate the number of excess students
            list_students = get_list_stutents_from_group(Data, group[0])  # Get the list of students in the group
            students = list_students[:n//2]  # Select half of the excess students
            
            new_group = get_new_group(Data, group[0])  # Get a new group for the excess students
            conn = sqlite3.connect(Data)  # Connect to the SQLite database
            for student in students:
                cursor = conn.cursor()  # Create a cursor object to execute SQL commands
                cursor.execute("UPDATE List_Groups_Students SET ID_COURSE = ? WHERE ID_STUDENT LIKE ? AND ID_COURSE LIKE ?;", 
                               (new_group, student[0], group[0]))
                conn.commit()  # Commit the transaction
            conn.close()  # Close the database connection
    return


def resolution_conflict_inverse(Data):
    """
    Resolves schedule conflicts by assigning students to new groups using the inverse method.

    Parameters:
    Data (str): Path to the SQLite database file.
    """
    conflicts = get_students_with_schedule_conflicts(Data)  # Get students with schedule conflicts
    for conflict in conflicts:
        new_group = get_new_group_inverse(Data, conflict[2])  # Get a new group using the inverse method
        conn = sqlite3.connect(Data)  # Connect to the SQLite database
        cursor = conn.cursor()  # Create a cursor object to execute SQL commands
        cursor.execute("UPDATE List_Groups_Students SET ID_COURSE = ? WHERE ID_STUDENT LIKE ? AND ID_COURSE LIKE ?;", 
                       (new_group, conflict[0], conflict[2]))
        conn.commit()  # Commit the transaction
        conn.close()  # Close the database connection
    return

def get_new_group_inverse(Data, id_group):
    """
    Determines a new group for a given group ID using the inverse method.

    Parameters:
    Data (str): Path to the SQLite database file.
    id_group (str): Group ID.

    Returns:
    str: New group ID.
    """
    match = re.search(r'G(\d+)_', id_group)  # Match the group number in the ID
    after_underscore = id_group[id_group.index('_'):]  # Get the substring after the underscore
    promo_list = id_group.split('_')[1]  # Get the promo list from the group ID
    language = id_group.split('_')[2]  # Get the language from the group ID
    
    if match:
        value_between_G_and_underscore = match.group(1)  # Extract the group number
    
    # Determine the new group based on the current group number using the inverse method
    if int(value_between_G_and_underscore) % 2 == 0:
        if int(value_between_G_and_underscore) == get_list_group(Data, language, promo_list):
            new_group = "G" + str(int(value_between_G_and_underscore) + 1) + after_underscore
        else:
            new_group = "G" + str(int(value_between_G_and_underscore) + 1) + after_underscore
    elif int(value_between_G_and_underscore) % 2 == 1:
        if int(value_between_G_and_underscore) == get_list_group(Data, language, promo_list):
            new_group = "G" + str(int(value_between_G_and_underscore) - 1) + after_underscore
        else:
            new_group = "G" + str(int(value_between_G_and_underscore) - 1) + after_underscore
    
    return new_group  # Return the new group ID