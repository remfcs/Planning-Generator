import sqlite3
import random

def Set_Availabilities(Data, DAYS, nb_H_per_day):
    conn = sqlite3.connect(Data)
    cursor = conn.cursor()
    for i in DAYS :
        for j in range (nb_H_per_day):
            #hour = "slot" + str(j+1)
            hour = j+1
            ID = str(i[:3]) +  "_" + str(hour)
            cursor.execute("INSERT INTO Availabilities VALUES (?,?,?);",(ID,i, hour ))
    conn.commit() 
    conn.close()
    return 


def Set_Rooms(Data, Rooms):
    conn = sqlite3.connect(Data)
    cursor = conn.cursor()
    for i in Rooms :
        ID = i
        cursor.execute("INSERT INTO Rooms VALUES (?,?);",(ID,i))
    conn.commit() 
    conn.close()
    return 

def Set_teachers(Data, list_teacher):
    conn = sqlite3.connect(Data)
    cursor = conn.cursor()

    teacher_emails = [teacher[2] for teacher in list_teacher]
    cursor.execute("DELETE FROM Teachers WHERE MAIL NOT IN (" + ",".join(["?"] * len(teacher_emails)) + ")", teacher_emails)

    for i in list_teacher :
        cursor.execute("SELECT count(*) FROM Teachers WHERE  NAME=? AND SURNAME=? AND MAIL = ? AND SUBJECT = ?", (i[0],i[1],i[2],i[3]))
        presence = cursor.fetchall()
        if presence[0][0] == 0  :
            ID = i[0][:3] + "_" + i[3][:3]
            cursor.execute("INSERT INTO Teachers VALUES (?,?,?,?,?);", (ID,i[0],i[1],i[2],i[3]))

    conn.commit() 
    conn.close()
    return 

def Set_table_de_jointure(Data, table, list_availibity_rooms):
    conn = sqlite3.connect(Data)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM '" + table + "';")
    for i in list_availibity_rooms :
        cursor.execute("INSERT INTO '" + table + "' VALUES (?,?,?);",(i[0],i[1], 0))
    conn.commit() 
    conn.close()



###############################################################################################
#   Fonctions de simulation des associations disponibilités & teachers/rooms/school_year      #
###############################################################################################

def get_list(Data):
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
    pairs = []
    for item1 in list1:
        selected_items = random.sample(list2, num_pairs)
        for item2 in selected_items:
            pairs.append((item1, item2))
    return pairs


