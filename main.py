import sqlite3
import pandas as pd
import numpy as np
import function_create_groups
import function_read_folder 
import function_database
import function_file_db
import back_up

Data = 'data/test.sqlite3'
depot_info_folder = './data/input_info'
db_path = './data/test.sqlite3' 
depot_note_folder ='./data/input_notes'
max_by_class = 16
#DAYS = ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday') 
DAYS = ('Thursday',) 
nb_slot = 6
promo_pair = [['1A','2A']]
Rooms = ('K03', 'K04', 'K05', 'M101', 'M102', 'M103', 'M104') 
list_teacher = [('MARTIN','Lucas','john.doe@example.com','ANGLAIS'),('BERNARD','Emma','emma.smith@example.com','ANGLAIS'),('DUBOIS','Gabriel','david.johnson@example.com','ANGLAIS'),('THOMAS','Léa','sarah.williams@example.com','ANGLAIS'),('ROBERT','Louis','james.brown@example.com','ANGLAIS'),('RICHARD','Chloé','emily.jones@example.com','ESPAGNOL'),('PETIT','Adam','michael.davis@example.com','ESPAGNOL'),('DURAND','Manon','olivia.miller@example.com','ESPAGNOL'),('LEROY','Hugo','robert.wilson@example.com','ESPAGNOL'),('MOREAU','Jade','sophia.moore@example.com','ALLEMAND'),('SIMON','Nathan','william.taylor@example.com','ALLEMAND'),('LAURENT','Inés','isabella.anderson@example.com','CHINOIS')]

#charge une df avec les infos des étudiants depuis le fichier info_student
df = function_read_folder.file_data_Student(depot_info_folder)

#Récupère les notes dans étudiants pour les mettre dans la df et sortir une df 'students_info' avec toutes les infos des étudiants
students_info = function_read_folder.add_student_grade(depot_note_folder, df)
#print(students_info.head())
def find_duplicate_emails(students_info):
    duplicate_emails = students_info.groupby('EMAIL').filter(lambda x: len(x) > 1)['EMAIL'].unique()
    return duplicate_emails

# Exemple d'utilisation
duplicate_emails = find_duplicate_emails(students_info)
#print("Emails en doublon :", duplicate_emails)

#crée le backup
back_up.backup(Data)

#supprime les données de la table student
function_database.delete_table_data(Data, "Student")

#charge les données des étudiants dans la table student
conn = sqlite3.connect(db_path)
function_database.insert_df_into_db(conn, students_info, "Student")

#supprimer et remplir la table 'Availabilities'
function_database.delete_table_data(Data, "Availabilities")
function_file_db.Set_Availabilities(Data, DAYS, nb_slot)

#supprimer et remplir la table 'Rooms'
function_database.delete_table_data(Data, "Rooms")
function_file_db.Set_Rooms(Data, Rooms)

#supprimer et remplir la table 'Teachers'
function_database.delete_table_data(Data, "Teachers")
function_file_db.Set_teachers(Data, list_teacher)

#simuler les tables de jointure de disponibilité
list_ID_Teacher, list_ID_room, list_ID_Availability, list_ID_Class = function_file_db.get_list(Data)

#list_availibity_teachers = function_file_db.create_random_pairs(list_ID_Teacher, list_ID_Availability,3)
#list_availibity_teachers =[('BER_ANG', 'Thu_slot3'), ('BER_ANG', 'Thu_slot1'), ('BER_ANG', 'Thu_slot2'),  ('DUB_ANG', 'Thu_slot1'), ('DUB_ANG', 'Thu_slot3'), ('DUB_ANG', 'Thu_slot2'),  ('DUR_ESP', 'Thu_slot1'), ('DUR_ESP', 'Thu_slot2'), ('DUR_ESP', 'Thu_slot3'),  ('LAU_CHI', 'Thu_slot3'), ('LAU_CHI', 'Thu_slot1'), ('LAU_CHI', 'Thu_slot2'),  ('LER_ESP', 'Thu_slot1'), ('LER_ESP', 'Thu_slot2'), ('LER_ESP', 'Thu_slot3'),  ('MAR_ANG', 'Thu_slot3'), ('MAR_ANG', 'Thu_slot2'), ('MAR_ANG', 'Thu_slot1'),  ('MOR_ALL', 'Thu_slot3'), ('MOR_ALL', 'Thu_slot2'), ('MOR_ALL', 'Thu_slot1'),  ('PET_ESP', 'Thu_slot2'), ('PET_ESP', 'Thu_slot1'), ('PET_ESP', 'Thu_slot3'),  ('RIC_ESP', 'Thu_slot1'), ('RIC_ESP', 'Thu_slot2'), ('RIC_ESP', 'Thu_slot3'),  ('ROB_ANG', 'Thu_slot2'), ('ROB_ANG', 'Thu_slot3'), ('ROB_ANG', 'Thu_slot1'),  ('SIM_ALL', 'Thu_slot3'), ('SIM_ALL', 'Thu_slot2'), ('SIM_ALL', 'Thu_slot1'),  ('THO_ANG', 'Thu_slot3'), ('THO_ANG', 'Thu_slot1'), ('THO_ANG', 'Thu_slot2')]
list_availibity_teachers =[('BER_ANG', 'Thu_slot3'), ('BER_ANG', 'Thu_slot1'), ('BER_ANG', 'Thu_slot2'),  ('DUB_ANG', 'Thu_slot1'), ('DUB_ANG', 'Thu_slot3'), ('DUB_ANG', 'Thu_slot2'),  ('DUR_ESP', 'Thu_slot1'), ('DUR_ESP', 'Thu_slot2'), ('DUR_ESP', 'Thu_slot3'),  ('LAU_CHI', 'Thu_slot3'), ('LAU_CHI', 'Thu_slot1'), ('LAU_CHI', 'Thu_slot2'),  ('LER_ESP', 'Thu_slot1'), ('LER_ESP', 'Thu_slot2'), ('LER_ESP', 'Thu_slot3'),  ('MAR_ANG', 'Thu_slot3'), ('MAR_ANG', 'Thu_slot2'), ('MAR_ANG', 'Thu_slot1'),  ('MOR_ALL', 'Thu_slot3'), ('MOR_ALL', 'Thu_slot2'), ('MOR_ALL', 'Thu_slot1'), ('ROB_ANG', 'Thu_slot2'), ('ROB_ANG', 'Thu_slot3'), ('ROB_ANG', 'Thu_slot1'), ('PET_ESP','Thu_slot1'), ('PET_ESP','Thu_slot2'),('RIC_ESP','Thu_slot3'), ('RIC_ESP','Thu_slot2')]
#list_availibity_rooms = function_file_db.create_random_pairs(list_ID_room, list_ID_Availability,6)
list_availibity_rooms = [('K03', 'Thu_slot1'), ('K03', 'Thu_slot2'), ('K03', 'Thu_slot3'), ('K04', 'Thu_slot1'), ('K04', 'Thu_slot3'), ('K04', 'Thu_slot2'), ('K05', 'Thu_slot3'), ('K05', 'Thu_slot2'), ('K05', 'Thu_slot1'), ('M101', 'Thu_slot1'), ('M101', 'Thu_slot2'), ('M101', 'Thu_slot3'), ('M102', 'Thu_slot3'), ('M102', 'Thu_slot2'), ('M102', 'Thu_slot1'), ('M103', 'Thu_slot1'), ('M103', 'Thu_slot2'), ('M103', 'Thu_slot3'), ('M104', 'Thu_slot1'), ('M104', 'Thu_slot2'), ('M104', 'Thu_slot3')]
#list_availibity_class = function_file_db.create_random_pairs(list_ID_Class,list_ID_Availability, 3)
list_availibity_class = [('1A', 'Thu_slot1'), ('1A', 'Thu_slot2'), ('1A', 'Thu_slot3')]

#Remplir les tables de jointure 
function_file_db.Set_table_de_jointure(Data, 'Availability_Rooms' ,list_availibity_rooms)
function_file_db.Set_table_de_jointure(Data, 'Availability_Teachers' ,list_availibity_teachers)
function_file_db.Set_table_de_jointure(Data, 'Availability_Class', list_availibity_class)

#supprime les données de la table groupe
function_database.delete_table_data(Data, "Courses")
function_database.delete_table_data(Data, "List_Groups_Students")

#AAAA FINIRRRR
#function_create_groups.make_groups_lv(Data, promo_pair)
function_create_groups.make_groups2(Data, promo_pair, max_by_class)


