import sqlite3
import pandas as pd
import numpy as np
import json
import os
import function_create_groups
import function_read_folder 
import function_database
import random
import back_up

Data = 'data/data.sqlite3'
depot_info_folder = './data/input_info'
db_path = './data/data.sqlite3' 
depot_note_folder ='./data/input_notes'
max_by_class = 16
nb_forecast_by_class = {
        '1A': 30,
        '2A' : 0
    }
#DAYS = ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday') 
DAYS = ('Wednesday', 'Thursday') 
nb_slot = 6
Rooms = ('K03', 'K04', 'K05', 'M101', 'M102', 'M103', 'M104') 
list_teacher = [('MARTIN','Lucas','john.doe@example.com','ANGLAIS'),('BERNARD','Emma','emma.smith@example.com','ANGLAIS'),('DUBOIS','Gabriel','david.johnson@example.com','ANGLAIS'),('THOMAS','Léa','sarah.williams@example.com','ANGLAIS'),('ROBERT','Louis','james.brown@example.com','ANGLAIS'),('RICHARD','Chloé','emily.jones@example.com','ESPAGNOL'),('PETIT','Adam','michael.davis@example.com','ESPAGNOL'),('DURAND','Manon','olivia.miller@example.com','ESPAGNOL'),('LEROY','Hugo','robert.wilson@example.com','ESPAGNOL'),('MOREAU','Jade','sophia.moore@example.com','ALLEMAND'),('SIMON','Nathan','william.taylor@example.com','ALLEMAND'),('LAURENT','Inés','isabella.anderson@example.com','CHINOIS')]


#charge une df avec les infos des étudiants depuis le fichier info_student
df = function_read_folder.file_data_Student(depot_info_folder)

#Récupère les notes dans étudiants pour les mettre dans la df et sortir une df 'students_info' avec toutes les infos des étudiants
students_info = function_read_folder.add_student_grade(depot_note_folder, df)

#crée le backup
back_up.backup(Data)

#supprime les données de la table student
function_database.delete_table_data(Data, "Student")

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

print(students_info)
#charge les données des étudiants dans la table student
conn = sqlite3.connect(db_path)
function_database.insert_df_into_db(conn, students_info, "Student")

#supprime les données de la table groupe
function_database.delete_table_data(Data, "Groups")

#AAAA FINIRRRR
#function_create_groups.made_LV2_groupe(Data,nb_forecast_by_class, max_by_class)

