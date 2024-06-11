import sqlite3
import pandas as pd
import numpy as np
from algo_feature import conflict_function, db_file_function, database_function, read_folder_function, create_groups_function
from back_up import back_up
import json
import os

"""
    À faire :
    # TODO faire le doc de la maintenance
"""

Data = 'data/database.sqlite3'

#depot_info_folder = './data/uploads/input_info'
#depot_note_folder ='./data/uploads/input_level'
#depot_info_folder = './data/uploads/input_info'
#depot_note_folder ='./data/uploads/input_level'

#depot_info_folder = './data/input_info'
#depot_note_folder ='./data/input_notes'
#depot_info_folder = './data/input_info'
#depot_note_folder ='./data/input_notes'

depot_info_folder = './data/xlsx/input_info'
depot_note_folder ='./data/xlsx/input_notes'

max_by_class = 19
DAYS = ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday') 
nb_slot = 6
promo_pair = {
    'ANGLAIS': [['1AFT', '1AFG', '1ABEE'],['2AFT', '2AFG', '2ABEE'], ['3AFG']],
    'ALLEMAND': [['1AFT', '2AFT', '1AFG', '2AFG'], ['3AFG']],
    'ESPAGNOL': [['1AFT', '2AFT', '1AFG', '2AFG'], ['3AFG']],
    'CHINOIS': [['1AFT', '2AFT','3AFG', '1AFG', '2AFG']],
    'ANGLAIS COMPLEMENTAIRE' : [['1AFT', '2AFT', '1ABEE', '2ABEE']],
    'DISPENSE D\'ANGLAIS' : [['1ABEE', '2ABEE']]
}


Rooms = ('K03', 'K04', 'K05', 'M101', 'M102', 'M103', 'M104', 'M01', 'M02') 
#list_teacher = [('MARTIN','Lucas','john.doe@example.com','ANGLAIS'),('BERNARD','Emma','emma.smith@example.com','ANGLAIS'),('DUBOIS','Gabriel','david.johnson@example.com','ANGLAIS'),('THOMAS','Léa','sarah.williams@example.com','ANGLAIS'),('ROBERT','Louis','james.brown@example.com','ANGLAIS'),('RICHARD','Chloé','emily.jones@example.com','ESPAGNOL'),('PETIT','Adam','michael.davis@example.com','ESPAGNOL'),('DURAND','Manon','olivia.miller@example.com','ESPAGNOL'),('LEROY','Hugo','robert.wilson@example.com','ESPAGNOL'),('MOREAU','Jade','sophia.moore@example.com','ALLEMAND'),('SIMON','Nathan','william.taylor@example.com','ALLEMAND'),('LAURENT','Inés','isabella.anderson@example.com','CHINOIS')]

#simuler les tables de jointure de disponibilité
list_ID_Teacher, list_ID_room, list_ID_Availability, list_ID_Class = db_file_function.get_list(Data)

#list_availability_teachers =[('BER_ANG', 'Thu_3'), ('BER_ANG', 'Thu_1'), ('BER_ANG', 'Thu_2'),  ('DUB_ANG', 'Thu_1'), ('DUB_ANG', 'Thu_3'), ('DUB_ANG', 'Thu_2'),  ('DUR_ESP', 'Thu_1'), ('DUR_ESP', 'Thu_2'),  ('LAU_CHI', 'Thu_3'), ('LAU_CHI', 'Thu_1'), ('LAU_CHI', 'Thu_2'), ('LER_ESP', 'Thu_2'), ('LER_ESP', 'Thu_3'),  ('MAR_ANG', 'Thu_3'), ('MAR_ANG', 'Thu_2'), ('MAR_ANG', 'Thu_1'),  ('MOR_ALL', 'Thu_3'), ('MOR_ALL', 'Thu_2'), ('MOR_ALL', 'Tue_1'), ('ROB_ANG', 'Thu_2'), ('ROB_ANG', 'Thu_3'), ('ROB_ANG', 'Thu_1'), ('PET_ESP','Thu_1'), ('PET_ESP','Thu_2'),('RIC_ESP','Thu_3'), ('RIC_ESP','Thu_2'), ('BER_ANG', 'Tue_3'), ('BER_ANG', 'Tue_1'), ('BER_ANG', 'Tue_2'),  ('DUB_ANG', 'Tue_1'), ('DUB_ANG', 'Tue_3'), ('DUB_ANG', 'Tue_2'),  ('DUR_ESP', 'Tue_1'), ('DUR_ESP', 'Tue_2'), ('LER_ESP', 'Tue_2'), ('LER_ESP', 'Tue_3'),  ('MAR_ANG', 'Tue_3'), ('MAR_ANG', 'Tue_2'), ('MAR_ANG', 'Tue_1'),  ('ROB_ANG', 'Tue_2'), ('ROB_ANG', 'Tue_3'), ('ROB_ANG', 'Tue_1'), ('PET_ESP','Tue_1'), ('PET_ESP','Tue_2'), ('RIC_ESP','Tue_3'), ('RIC_ESP','Tue_2')]
#list_availibity_rooms = function_file_db.create_random_pairs(list_ID_room, list_ID_Availability,6)
list_availibity_rooms = [('K03', 'Thu_2'), ('K03', 'Thu_1'), ('K03', 'Thu_3'), ('K04', 'Thu_1'), ('K04', 'Thu_3'), ('K04', 'Thu_2'), ('K05', 'Thu_3'), ('K05', 'Thu_2'), ('K05', 'Thu_1'), ('M101', 'Thu_3'), ('M101', 'Thu_2'), ('M101', 'Thu_1'), ('M102', 'Thu_3'), ('M102', 'Thu_2'), ('M102', 'Thu_1'), ('M103', 'Thu_1'), ('M103', 'Thu_2'), ('M103', 'Thu_3'), ('M104', 'Thu_1'), ('M104', 'Thu_2'), ('M104', 'Thu_3'), ('M01', 'Thu_1'), ('M01', 'Thu_2'), ('M01', 'Thu_3'), ('M02', 'Thu_3'), ('M02', 'Thu_2'), ('M02', 'Thu_1'), ('K03', 'Tue_2'), ('K03', 'Tue_1'), ('K03', 'Tue_3'), ('K04', 'Tue_1'), ('K04', 'Tue_3'), ('K04', 'Tue_2'), ('K05', 'Tue_3'), ('K05', 'Tue_2'), ('K05', 'Tue_1'), ('M101', 'Tue_3'), ('M101', 'Tue_2'), ('M101', 'Tue_1'), ('M102', 'Tue_3'), ('M102', 'Tue_2'), ('M102', 'Tue_1'), ('M103', 'Tue_1'), ('M103', 'Tue_2'), ('M103', 'Tue_3'), ('M104', 'Tue_1'), ('M104', 'Tue_2'), ('M104', 'Tue_3'), ('M01', 'Tue_1'), ('M01', 'Tue_2'), ('M01', 'Tue_3'), ('M02', 'Tue_3'), ('M02', 'Tue_2'), ('M02', 'Tue_1')]
#list_availibity_class = function_file_db.create_random_pairs(list_ID_Class,list_ID_Availability, 3)
#list_availibity_class = [('1A', 'Thu_1'), ('1A', 'Thu_2'), ('1A', 'Thu_3'),('2A', 'Thu_1'), ('2A', 'Thu_2'), ('2A', 'Thu_3')]
#list_availibity_class = [('1A', 'Thu_1'), ('1A', 'Thu_2'), ('1A', 'Thu_3'),('2A', 'Thu_1'), ('2A', 'Thu_2'), ('3A', 'Thu_3'),('3A', 'Tue_1'), ('3A', 'Tue_2'), ('3A', 'Tue_3'), ('1AFG', 'Thu_1'), ('1AFG', 'Thu_2'), ('1AFG', 'Thu_3'), ('2AFG', 'Thu_1'), ('2AFG', 'Thu_2'), ('2AFG', 'Thu_3'), ('BEE', 'Thu_1'), ('BEE', 'Thu_2'), ('BEE', 'Thu_3')]
#list_availibity_class = [('1A', 'Thu_1'), ('1A', 'Thu_2'), ('1A', 'Thu_3'),('2A', 'Thu_1'), ('2A', 'Thu_2'),('3A', 'Tue_1'), ('3A', 'Tue_2'), ('3A', 'Tue_3'), ('1AFG', 'Thu_1'), ('1AFG', 'Thu_2'), ('1AFG', 'Thu_3'), ('2AFG', 'Thu_1'), ('2AFG', 'Thu_2'), ('2AFG', 'Thu_3'), ('BEE', 'Thu_1'), ('BEE', 'Thu_2'), ('BEE', 'Thu_3'), ('3AFG', 'Tue_1'), ('3AFG', 'Tue_2'), ('3AFG', 'Tue_3')]


# Example usage
json_path = 'data/uploads/teachers.json'
list_teacher, list_availability_teachers = read_folder_function.load_teachers(json_path)
#print(list_teacher, list_availability_teachers)
json_path = 'data/uploads/promo_availabilities.json'
list_class, list_availibity_class = read_folder_function.load_class(json_path)

#charge une df avec les infos des étudiants depuis le fichier info_student
df = read_folder_function.file_data_Student(depot_info_folder)

#Récupère les notes dans étudiants pour les mettre dans la df et sortir une df 'students_info' avec toutes les infos des étudiants
students_info = read_folder_function.add_student_grade(depot_note_folder, df)

#crée le backup
back_up.backup(Data)

#supprime les données de la table student
database_function.delete_table_data(Data, "Student")

#charge les données des étudiants dans la table student
conn = sqlite3.connect(Data)
students_info.rename(columns={'FIRSTNAME': 'SURNAME'}, inplace=True)
students_info = students_info.drop_duplicates(subset='EMAIL', keep="first")

database_function.insert_df_into_db(conn, students_info, "Student")


#supprimer et remplir la table 'Availabilities'
database_function.delete_table_data(Data, "Availabilities")
db_file_function.Set_Availabilities(Data, DAYS, nb_slot)

#supprimer et remplir la table 'Rooms'
database_function.delete_table_data(Data, "Rooms")
db_file_function.Set_Rooms(Data, Rooms)

#supprimer et remplir la table 'Teachers'
database_function.delete_table_data(Data, "Teachers")
db_file_function.Set_teachers(Data, list_teacher)

#Remplir les tables de jointure 
db_file_function.Set_table_de_jointure(Data, 'Availability_Rooms' ,list_availibity_rooms)
db_file_function.Set_table_de_jointure(Data, 'Availability_Teachers' ,list_availability_teachers)
db_file_function.Set_table_de_jointure(Data, 'Availability_Class', list_availibity_class)

#supprime les données de la table groupe
database_function.delete_table_data(Data, "Courses")
database_function.delete_table_data(Data, "List_Groups_Students")

#Créer les groupes 
create_groups_function.make_groups(Data, promo_pair, max_by_class) 

create_groups_function.make_association(Data, promo_pair)

conflict_function.resolve_conflict(Data)

database_function.set_group_name(Data)