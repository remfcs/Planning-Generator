####################################################################################
#                              Reset database Functions                            #
####################################################################################
# Provides functionalities to detect and resolve scheduling conflicts for students #
# enrolled in 2 courses simultaneously. It includes detecting conflicts, updating  #
# student groups, and resolving conflicts by exchanging students between groups.   #
####################################################################################

# --------------------------------------------------------------------------------
# Modules:
# --------------------------------------------------------------------------------
# 1. Delete_one_table:
#    - Drop one specific table from a databse.
#
# 2. list_tables:
#    - Retrieves the list of table for database.
#
# 3. Delete_all_tables:
#    - Drop all the table from a databse.
#
# 4. Create_tables:
#    - Create all the table needed in a specifique database.
# --------------------------------------------------------------------------------

# --------------------------------------------------------------------------------
# Dependencies:
# --------------------------------------------------------------------------------
# - sqlite3
# --------------------------------------------------------------------------------

import sqlite3

# Path to the SQLite database file
Data = './data/database.sqlite3'

def Delete_one_table(Data, name_table):
    """
    Deletes a single table from the SQLite database.

    Parameters:
    Data (str): Path to the SQLite database file.
    name_table (str): Name of the table to be deleted.

    Returns:
    list: Names of the remaining tables in the database.
    """
    # Connect to the SQLite database
    conn = sqlite3.connect(Data)
    cursor = conn.cursor()

    # Execute the SQL command to drop the specified table
    cursor.execute("DROP TABLE " + name_table + ";")

    # Fetch the names of the remaining tables
    tables = cursor.fetchall()

    # Close the connection
    conn.close()

    # Return the list of remaining table names
    return [table[0] for table in tables]

def list_tables(Data):
    """
    Lists all tables in the SQLite database.

    Parameters:
    Data (str): Path to the SQLite database file.

    Returns:
    list: Names of all tables in the database.
    """
    # Connect to the SQLite database
    conn = sqlite3.connect(Data)
    cursor = conn.cursor()

    # Execute the SQL command to retrieve table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")

    # Fetch all table names
    tables = cursor.fetchall()

    # Close the connection
    conn.close()

    # Return the list of table names
    return [table[0] for table in tables]

def Delete_all_tables(Data):
    """
    Deletes all tables from the SQLite database except 'sqlite_sequence'.

    Parameters:
    Data (str): Path to the SQLite database file.
    """
    # Connect to the SQLite database
    conn = sqlite3.connect(Data)

    # Retrieve the list of all tables
    for i in list_tables(Data):
        cursor = conn.cursor()

        # Skip the 'sqlite_sequence' table, which is used for autoincrement keys
        if i != 'sqlite_sequence':
            # Execute the SQL command to drop the table
            cursor.execute("DROP TABLE " + i + ";")

    # Close the connection
    conn.close()

# Delete all tables in the database
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

## intersection table

# create table 'List_Groups_Students'
    cursor.execute("CREATE TABLE IF NOT EXISTS List_Groups_Students (ID_COURSE Varchar (50) , ID_STUDENT Varchar(50) , FOREIGN KEY(ID_COURSE) REFERENCES Courses(ID_COURSE), FOREIGN KEY(ID_STUDENT) REFERENCES Student(EMAIL));")
# create table 'Availability_Teachers'
    cursor.execute("CREATE TABLE IF NOT EXISTS Availability_Teachers (ID_Teacher INT, ID_Availability INT, ACTIVE BOOLEAN DEFAULT 0, FOREIGN KEY(ID_Teacher) REFERENCES Teachers(ID_teacher), FOREIGN KEY(ID_Availability) REFERENCES Availabilities(ID_Availability));")
# create table 'Availability_Rooms'
    cursor.execute("CREATE TABLE IF NOT EXISTS Availability_Rooms (ID_Room INT, ID_Availability INT, ACTIVE BOOLEAN DEFAULT 0, FOREIGN KEY(ID_Room) REFERENCES Rooms(ID_room), FOREIGN KEY(ID_Availability) REFERENCES Availabilities(ID_Availability));")
# create table 'Availability_Class'
    cursor.execute("CREATE TABLE IF NOT EXISTS Availability_Class (ID_Class VARCHAR(5), ID_Availability INT, ACTIVE BOOLEAN DEFAULT 0, FOREIGN KEY(ID_Class) REFERENCES Student(CLASSE), FOREIGN KEY(ID_Availability) REFERENCES Availabilities(ID_Availability));")

    cursor.fetchall()
    conn.commit()
    conn.close()

Create_tables(Data)
