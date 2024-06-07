import sqlite3
import pandas as pd
import numpy as np
from algo_feature import function_conflict, function_file_db, function_database, function_read_folder, function_create_groups
from back_up import back_up
import json
import os

'''
    À faire :

    - refaire numberclass
    - phoenix
    - mapper les colonnes dans function_read_folder
    # ? Documenter toutes les fonctions
    # ? faire le doc de la maintenance        
    - rajouter les 3A ft
    - 1A, 2A et 3A peuvent avoir cours en même temps de Allemand et Chinois !
    - améliorer la balance des conflits
    - 
''' 

Data = 'data/database.sqlite3'

#depot_info_folder = './data/uploads/input_info'
#depot_note_folder ='./data/uploads/input_level'

depot_info_folder = './data/input_info'
depot_note_folder ='./data/input_notes'

max_by_class = 16

DAYS = ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday') 

nb_slot = 6
promo_pair = [['1A','2A', '1AFG'], ['3A']]
Rooms = ('K03', 'K04', 'K05', 'M101', 'M102', 'M103', 'M104', 'M01', 'M02') 
list_teacher = [('MARTIN','Lucas','john.doe@example.com','ANGLAIS'),('BERNARD','Emma','emma.smith@example.com','ANGLAIS'),('DUBOIS','Gabriel','david.johnson@example.com','ANGLAIS'),('THOMAS','Léa','sarah.williams@example.com','ANGLAIS'),('ROBERT','Louis','james.brown@example.com','ANGLAIS'),('RICHARD','Chloé','emily.jones@example.com','ESPAGNOL'),('PETIT','Adam','michael.davis@example.com','ESPAGNOL'),('DURAND','Manon','olivia.miller@example.com','ESPAGNOL'),('LEROY','Hugo','robert.wilson@example.com','ESPAGNOL'),('MOREAU','Jade','sophia.moore@example.com','ALLEMAND'),('SIMON','Nathan','william.taylor@example.com','ALLEMAND'),('LAURENT','Inés','isabella.anderson@example.com','CHINOIS')]

#simuler les tables de jointure de disponibilité
list_ID_Teacher, list_ID_room, list_ID_Availability, list_ID_Class = function_file_db.get_list(Data)
list_availability_teachers =[('BER_ANG', 'Thu_3'), ('BER_ANG', 'Thu_1'), ('BER_ANG', 'Thu_2'),  ('DUB_ANG', 'Thu_1'), ('DUB_ANG', 'Thu_3'), ('DUB_ANG', 'Thu_2'),  ('DUR_ESP', 'Thu_1'), ('DUR_ESP', 'Thu_2'),  ('LAU_CHI', 'Thu_3'), ('LAU_CHI', 'Thu_1'), ('LAU_CHI', 'Thu_2'), ('LER_ESP', 'Thu_2'), ('LER_ESP', 'Thu_3'),  ('MAR_ANG', 'Thu_3'), ('MAR_ANG', 'Thu_2'), ('MAR_ANG', 'Thu_1'),  ('MOR_ALL', 'Thu_3'), ('MOR_ALL', 'Thu_2'), ('MOR_ALL', 'Thu_1'), ('ROB_ANG', 'Thu_2'), ('ROB_ANG', 'Thu_3'), ('ROB_ANG', 'Thu_1'), ('PET_ESP','Thu_1'), ('PET_ESP','Thu_2'),('RIC_ESP','Thu_3'), ('RIC_ESP','Thu_2')]
#list_availibity_rooms = function_file_db.create_random_pairs(list_ID_room, list_ID_Availability,6)
list_availibity_rooms = [('K03', 'Thu_2'), ('K03', 'Thu_1'), ('K03', 'Thu_3'), ('K04', 'Thu_1'), ('K04', 'Thu_3'), ('K04', 'Thu_2'), ('K05', 'Thu_3'), ('K05', 'Thu_2'), ('K05', 'Thu_1'), ('M101', 'Thu_3'), ('M101', 'Thu_2'), ('M101', 'Thu_1'), ('M102', 'Thu_3'), ('M102', 'Thu_2'), ('M102', 'Thu_1'), ('M103', 'Thu_1'), ('M103', 'Thu_2'), ('M103', 'Thu_3'), ('M104', 'Thu_1'), ('M104', 'Thu_2'), ('M104', 'Thu_3'), ('M01', 'Thu_1'), ('M01', 'Thu_2'), ('M01', 'Thu_3'), ('M02', 'Thu_3'), ('M02', 'Thu_2'), ('M02', 'Thu_1')]
#list_availibity_class = function_file_db.create_random_pairs(list_ID_Class,list_ID_Availability, 3)
list_availibity_class = [('1A', 'Thu_1'), ('1A', 'Thu_2'), ('1A', 'Thu_3')]


# Example usage
#json_path = 'data/uploads/teachers.json'
#list_teacher, list_availability_teachers = function_read_folder.load_teachers(json_path)
#print(list_teacher)


#charge une df avec les infos des étudiants depuis le fichier info_student
df = function_read_folder.file_data_Student(depot_info_folder)

#Récupère les notes dans étudiants pour les mettre dans la df et sortir une df 'students_info' avec toutes les infos des étudiants
students_info = function_read_folder.add_student_grade(depot_note_folder, df)

#crée le backup
back_up.backup(Data)

#supprime les données de la table student
function_database.delete_table_data(Data, "Student")

#charge les données des étudiants dans la table student
conn = sqlite3.connect(Data)
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

#Remplir les tables de jointure 
function_file_db.Set_table_de_jointure(Data, 'Availability_Rooms' ,list_availibity_rooms)
function_file_db.Set_table_de_jointure(Data, 'Availability_Teachers' ,list_availability_teachers)
function_file_db.Set_table_de_jointure(Data, 'Availability_Class', list_availibity_class)

#supprime les données de la table groupe
function_database.delete_table_data(Data, "Courses")
function_database.delete_table_data(Data, "List_Groups_Students")

#AAAA FINIRRRR
#function_create_groups.make_groups_lv(Data, promo_pair)
function_create_groups.make_groups(Data, promo_pair, max_by_class) # ! à revoir 
function_create_groups.make_association(Data, promo_pair)

def boucle(m,l):
    n=0
    while n !=2:
        #standart
        for i in range (0,m):
            function_conflict.resolution_conflict(Data)
            function_conflict.balance_groups(Data, max_by_class)

        #changement pour eviter les boucles infinies
        for i in range (0,l):   
            function_conflict.resolution_conflict_inverse(Data)
            function_conflict.balance_groups(Data, max_by_class)
        n +=1
    # affichage
    print(function_conflict.get_nb_student_by_group(Data))
    print(len(function_conflict.get_students_with_schedule_conflicts(Data)))
    print(function_conflict.get_students_with_schedule_conflicts(Data))
    return

####       Meilleur compromis trouvé        #####

boucle(6,5)