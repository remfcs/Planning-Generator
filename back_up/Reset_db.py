import sqlite3

Data = 'data/test.sqlite3'


def Delete_one_table(Data, name_table):
    conn = sqlite3.connect(Data)
    cursor = conn.cursor()
    cursor.execute("DROP TABLE " + name_table + ";")
    tables = cursor.fetchall()
    conn.close()
    return [table[0] for table in tables]

def list_tables(Data):
    conn = sqlite3.connect(Data)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    conn.close()
    return [table[0] for table in tables]

def Delete_all_tables(Data):
    conn = sqlite3.connect(Data)
    for i in list_tables(Data):
        cursor = conn.cursor()
        if i != 'sqlite_sequence':
            cursor.execute("DROP TABLE " + i + ";")
    conn.close()
    return 


Delete_all_tables(Data)


def Create_tables(filename):
    conn = sqlite3.connect(filename)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

# create table 'Student' 
    #cursor.execute("CREATE TABLE IF NOT EXISTS Student(EMAIL Varchar (50), NAME Varchar (50), SURNAME Varchar (50), SCHOOL_YEAR  Varchar (50), LV1 Varchar (50), GRADE_LV1 Float, GROUP_LV1 Varchar (50),LV2 Varchar (50),GRADE_LV2 Float,GROUP_LV2 Varchar (50),REDUCED_EXAM Bool,STATUS Varchar (50) ,CONSTRAINT Student_PK PRIMARY KEY (EMAIL));")
    cursor.execute("CREATE TABLE IF NOT EXISTS Student(EMAIL Varchar (50), NAME Varchar (50), SURNAME Varchar (50), SCHOOL_YEAR  Varchar (50), LV1 Varchar (50), GRADE_LV1 Float, LV2 Varchar (50),GRADE_LV2 Float,REDUCED_EXAM Bool,STATUS Varchar (50) ,CONSTRAINT Student_PK PRIMARY KEY (EMAIL));")
# create table 'List_Groups_Students'
    cursor.execute("CREATE TABLE IF NOT EXISTS List_Groups_Students (ID_COURSE Varchar (50), ID_STUDENT Varchar(50) , FOREIGN KEY(ID_COURSE) REFERENCES Courses(ID_COURSE), FOREIGN KEY(ID_STUDENT) REFERENCES Student(EMAIL));")
# create table 'Teachers'  
    cursor.execute("CREATE TABLE IF NOT EXISTS Teachers(ID_TEACHER Varchar (50) ,NAME Varchar (50),SURNAME Varchar (50) ,MAIL Varchar (50) ,SUBJECT Varchar (50) ,CONSTRAINT Teachers_PK PRIMARY KEY (ID_TEACHER));")
# create table 'Availabilities'
    cursor.execute("CREATE TABLE IF NOT EXISTS Availabilities(ID_AVAILABILITY Varchar (50),DAY Varchar (50) ,HOUR Varchar (50) ,CONSTRAINT Availabilities_PK PRIMARY KEY (ID_AVAILABILITY));")
# create table 'Rooms'
    cursor.execute("CREATE TABLE IF NOT EXISTS Rooms(ID_ROOM Varchar (50),NAME Varchar (50),CONSTRAINT Rooms_PK PRIMARY KEY (ID_ROOM));")
# create table 'Courses'
    cursor.execute("CREATE TABLE IF NOT EXISTS Courses(ID_COURSE Varchar (50),ID_GROUP Varchar (50) ,ID_TEACHER Varchar (50) ,LANGUAGE VARCHAR (50) ,ID_ROOM Varchar (50) ,ID_AVAILABILITY Varchar (50), PROMO VARCHAR(50) ,CONSTRAINT Courses_PK PRIMARY KEY (ID_COURSE));")

## table de jointures

# create table 'List_Groups_Students'
    cursor.execute("CREATE TABLE IF NOT EXISTS List_Groups_Students (ID_COURSE Varchar (50) , ID_STUDENT Varchar(50) , FOREIGN KEY(ID_COURSE) REFERENCES Courses(ID_COURSE), FOREIGN KEY(ID_STUDENT) REFERENCES Student(EMAIL));")
# create table 'Availability_Teachers'
    cursor.execute("CREATE TABLE IF NOT EXISTS Availability_Teachers (ID_Teacher INT, ID_Availability INT, FOREIGN KEY(ID_Teacher) REFERENCES Teachers(ID_teacher), FOREIGN KEY(ID_Availability) REFERENCES Availabilities(ID_Availability));")
# create table 'Availability_Rooms'
    cursor.execute("CREATE TABLE IF NOT EXISTS Availability_Rooms (ID_Room INT, ID_Availability INT, FOREIGN KEY(ID_Room) REFERENCES Rooms(ID_room), FOREIGN KEY(ID_Availability) REFERENCES Availabilities(ID_Availability));")
# create table 'Availability_Class'
    cursor.execute("CREATE TABLE IF NOT EXISTS Availability_Class (ID_Class VARCHAR(5), ID_Availability INT, FOREIGN KEY(ID_Class) REFERENCES Student(CLASSE), FOREIGN KEY(ID_Availability) REFERENCES Availabilities(ID_Availability));")

    cursor.fetchall()
    conn.commit()
    conn.close()

Create_tables(Data)
