####################################################################################
#                            Database File Functions                               #
####################################################################################
# Provides functionalities to set up database tables, including availabilities,    #
# rooms, teachers, and joint tables. It also includes functions for simulating     #
# random associations between these entities.                                       #
####################################################################################

# --------------------------------------------------------------------------------
# Modules:
# --------------------------------------------------------------------------------
# 1. Set_Availabilities:
#    - Sets availability slots for given days and hours per day.
#
# 2. Set_Rooms:
#    - Sets room information in the database.
#
# 3. Set_teachers:
#    - Sets teacher information in the database.
#
# 4. Set_table_de_jointure:
#    - Sets up joint tables for availabilities and rooms.
#
# 5. get_list:
#    - Retrieves lists of teacher IDs, room IDs, availability IDs, and class IDs.
#
# 6. create_random_pairs:
#    - Creates random pairs between two lists.
# --------------------------------------------------------------------------------

# --------------------------------------------------------------------------------
# Dependencies:
# --------------------------------------------------------------------------------
# - sqlite3
# - random
# --------------------------------------------------------------------------------

import sqlite3
import random

def Set_Availabilities(Data, DAYS, nb_H_per_day):
    """
    Sets availability slots for given days and hours per day.
    
    Args:
        Data (str): The path to the SQLite database file.
        DAYS (list): List of days.
        nb_H_per_day (int): Number of hours per day.
    """
    conn = sqlite3.connect(Data)
    cursor = conn.cursor()
    for i in DAYS:
        for j in range(nb_H_per_day):
            hour = j + 1
            ID = str(i[:3]) + "_" + str(hour)
            cursor.execute("INSERT INTO Availabilities VALUES (?,?,?);", (ID, i, hour))
    conn.commit()
    conn.close()

def Set_Rooms(Data, Rooms):
    """
    Sets room information in the database.
    
    Args:
        Data (str): The path to the SQLite database file.
        Rooms (list): List of room identifiers.
    """
    conn = sqlite3.connect(Data)
    cursor = conn.cursor()
    for i in Rooms:
        ID = i
        cursor.execute("INSERT INTO Rooms VALUES (?,?);", (ID, i))
    conn.commit()
    conn.close()

def Set_teachers(Data, list_teacher):
    """
    Sets teacher information in the database.
    
    Args:
        Data (str): The path to the SQLite database file.
        list_teacher (list): List of teacher information tuples (name, surname, email, subject).
    """
    conn = sqlite3.connect(Data)
    cursor = conn.cursor()
    
    teacher_emails = [teacher[2] for teacher in list_teacher]
    cursor.execute("DELETE FROM Teachers WHERE MAIL NOT IN (" + ",".join(["?"] * len(teacher_emails)) + ")", teacher_emails)
    
    for i in list_teacher:
        cursor.execute("SELECT count(*) FROM Teachers WHERE NAME=? AND SURNAME=? AND MAIL = ? AND SUBJECT = ?", (i[0], i[1], i[2], i[3]))
        presence = cursor.fetchall()
        if presence[0][0] == 0:
            ID = i[0][:3] + "_" + i[3][:3]
            cursor.execute("INSERT INTO Teachers VALUES (?,?,?,?,?);", (ID, i[0], i[1], i[2], i[3]))
    
    conn.commit()
    conn.close()

def Set_table_de_jointure(Data, table, list_availibity_rooms):
    """
    Sets up joint tables for availabilities and rooms.
    
    Args:
        Data (str): The path to the SQLite database file.
        table (str): The name of the joint table.
        list_availibity_rooms (list): List of availability-room associations.
    """
    conn = sqlite3.connect(Data)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM '" + table + "';")
    for i in list_availibity_rooms:
        cursor.execute("INSERT INTO '" + table + "' VALUES (?,?,?);", (i[0], i[1], 0))
    conn.commit()
    conn.close()


###############################################################################################
#   Fonctions de simulation des associations disponibilités & teachers/rooms/school_year      #
###############################################################################################

def get_list(Data):
    """
    Retrieves lists of teacher IDs, room IDs, availability IDs, and class IDs.
    
    Args:
        Data (str): The path to the SQLite database file.
        
    Returns:
        tuple: Lists of teacher IDs, room IDs, availability IDs, and class IDs.
    """
    conn = sqlite3.connect(Data)
    cursor = conn.cursor()
    cursor.execute("SELECT ID_Teacher FROM Teachers;")
    list_ID_Teacher = cursor.fetchall()
    list_ID_Teacher = [row[0] for row in list_ID_Teacher]
    
    cursor.execute("SELECT ID_room FROM Rooms;")
    list_ID_room = cursor.fetchall()
    list_ID_room = [row[0] for row in list_ID_room]
    
    cursor.execute("SELECT ID_Availability FROM Availabilities;")
    list_ID_Availability = cursor.fetchall()
    list_ID_Availability = [row[0] for row in list_ID_Availability]
    
    cursor.execute("SELECT DISTINCT(SCHOOL_YEAR) FROM Student;")
    list_ID_Class = cursor.fetchall()
    list_ID_Class = [row[0] for row in list_ID_Class]
    
    conn.close()
    return list_ID_Teacher, list_ID_room, list_ID_Availability, list_ID_Class

def create_random_pairs(list1, list2, num_pairs):
    """
    Creates random pairs between two lists.
    
    Args:
        list1 (list): The first list.
        list2 (list): The second list.
        num_pairs (int): The number of pairs to create.
        
    Returns:
        list: The list of created pairs.
    """
    pairs = []
    for item1 in list1:
        selected_items = random.sample(list2, num_pairs)
        for item2 in selected_items:
            pairs.append((item1, item2))
    return pairs