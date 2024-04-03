import sqlite3
import pandas as pd
import numpy as np
import json
import os
import shutil


Data = 'data/data.sqlite3'
depot_info_folder = './data/input_info'
depot_note_folder ='./data/input_notes'
nb_by_class = 16
nb_forecast_by_class = {
        '1A': 30,
        '2A' : 0
    }
#DAYS = ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday') 
DAYS = ('Wednesday', 'Thursday') 
nb_slot = 6
Rooms = ('K03', 'K04', 'K05', 'M101', 'M102', 'M103', 'M104') 
list_teacher = [('MARTIN','Lucas','john.doe@example.com','ANGLAIS'),('BERNARD','Emma','emma.smith@example.com','ANGLAIS'),('DUBOIS','Gabriel','david.johnson@example.com','ANGLAIS'),('THOMAS','Léa','sarah.williams@example.com','ANGLAIS'),('ROBERT','Louis','james.brown@example.com','ANGLAIS'),('RICHARD','Chloé','emily.jones@example.com','ESPAGNOL'),('PETIT','Adam','michael.davis@example.com','ESPAGNOL'),('DURAND','Manon','olivia.miller@example.com','ESPAGNOL'),('LEROY','Hugo','robert.wilson@example.com','ESPAGNOL'),('MOREAU','Jade','sophia.moore@example.com','ALLEMAND'),('SIMON','Nathan','william.taylor@example.com','ALLEMAND'),('LAURENT','Inés','isabella.anderson@example.com','CHINOIS')]
import random


# Fonction pour supprimer toutes les données d'une table donnée
def Delete_data_table(filename, table):
    # Connexion à la base de données
    conn = sqlite3.connect(filename)
    cursor = conn.cursor()
    # Exécution de la requête SQL pour supprimer toutes les lignes de la table spécifiée
    cursor.execute("DELETE FROM '" + table + "';")
    # Commit des changements dans la base de données
    conn.commit() 
    # Fermeture de la connexion à la base de données
    conn.close()
    # La fonction ne retourne rien, elle modifie la base de données directement

def backup(Data):
    try:
        # Construction du nom de fichier pour la sauvegarde en ajoutant un préfixe "backup_" au nom du fichier de base de données
        name = "backup_" + os.path.splitext(os.path.basename(Data))[0]
        rename_data = os.path.join(os.path.dirname(Data), name) + ".sqlite3"
        # Copie du fichier de base de données vers la sauvegarde
        shutil.copy2(Data, rename_data)
    except FileNotFoundError:
        # Gestion de l'erreur si le fichier source n'existe pas
        print("Le fichier source n'existe pas.")
    except PermissionError:
        # Gestion de l'erreur si la permission est refusée pour copier ou renommer le fichier
        print("Permission refusée pour copier ou renommer le fichier.")
    except Exception as e:
        # Gestion de toutes les autres erreurs possibles
        print(f"Une erreur s'est produite : {e}")

# Appel de la fonction pour créer une sauvegarde du fichier de base de données
backup(Data)
# Appel de la fonction pour supprimer toutes les données de la table "Student"
Delete_data_table(Data, "Student")


# L'appel de fonction ci-dessous est commenté, donc il est actuellement désactivé.
# Si vous souhaitez supprimer toutes les données de la table "Groups", retirez le "#" pour activer cet appel de fonction.
# Delete_data_table(Data, "Groups")
# Importation des modules nécessaires

# Fonction pour restaurer une sauvegarde du fichier de base de données
def restor_backup(Data):
    try:
        # Construction du nom de fichier de la sauvegarde en ajoutant un préfixe "backup_" au nom du fichier de base de données
        name = "backup_" + os.path.splitext(os.path.basename(Data))[0]
        rename_data = os.path.join(os.path.dirname(Data), name) + ".sqlite3"
        print(rename_data)
        # Vérification de l'existence de la sauvegarde
        if os.path.exists(rename_data):
            # Suppression du fichier de base de données actuel
            os.remove(Data)
            # Renommage de la sauvegarde pour restaurer le fichier de base de données
            os.rename(rename_data, Data)
        else:
            # Affichage d'un message d'erreur si aucune sauvegarde n'est trouvée
            print(f"Impossible, there is no backup.")
            return False
    except FileNotFoundError:
        # Gestion de l'erreur si le fichier source n'existe pas
        print("Le fichier n'existe pas.")
    except PermissionError:
        # Gestion de l'erreur si la permission est refusée pour supprimer ou renommer le fichier
        print("Permission refusée pour supprimer le fichier.")
    except Exception as e:
        # Gestion de toutes les autres erreurs possibles
        print(f"Une erreur s'est produite : {e}")

# Appel de la fonction pour restaurer une sauvegarde du fichier de base de données
#restor_backup(Data)


def file_data_Student(depot_info_folder, db_path):
    conn = sqlite3.connect(db_path)
    desired_table_name = 'Student'
    for file in [f for f in os.listdir(depot_info_folder)]:
        if os.path.splitext(os.path.basename(file))[0] == 'Info_student' :
            db_column_mapping = {
                'Nom': 'NAME',
                'Prénom': 'SURNAME',
                'mail': 'EMAIL',
                'Class': 'CLASS'}

            if file.endswith('.csv'):
                csv_file_path = os.path.join(depot_info_folder, file)
                df = pd.read_csv(csv_file_path, encoding='utf-8-sig')                
                df.rename(columns=db_column_mapping, inplace=True)
                df = df[list(db_column_mapping.values())]
                df.to_sql(desired_table_name, conn, if_exists='append', index=False)

            elif file.endswith('.json'):
                json_file_path = os.path.join(depot_info_folder, file)
                with open(json_file_path, 'r', encoding='utf-8-sig') as json_file:
                    data = json.load(json_file)
                    transformed_data = []
                    for item in data:
                        transformed_item = {db_column: item.get(json_field) for json_field, db_column in db_column_mapping.items()}
                        transformed_data.append(transformed_item)
                    df = pd.DataFrame(transformed_data)
                    df.to_sql(desired_table_name, conn, if_exists='append', index=False)

            elif file.endswith('.xlsx'):
                xlsx_file_path = os.path.join(depot_info_folder, file)
                df = pd.read_excel(xlsx_file_path, header=0, usecols=["Nom", "Prénom", "mail", "Class"], skiprows=[0], )                
                df.rename(columns=db_column_mapping, inplace=True)
                df = df[list(db_column_mapping.values())]
                df.to_sql(desired_table_name, conn, if_exists='append', index=False)

            else:
                print(f"Format de fichier non pris en charge: {file}")

        elif os.path.splitext(os.path.basename(file))[0] == 'Sondage_LV2' :
            db_column_mapping = {
                'Nom': 'NAME',
                'Prénom': 'SURNAME',
                'mail': 'EMAIL',
                'Langues' : 'LV2'
            }
            if file.endswith('.csv'):
                csv_file_path = os.path.join(depot_info_folder, file)
                with open(csv_file_path, 'r', encoding='utf-8-sig') as csvfile:
                    csv_reader = pd.read_csv(csv_file_path, encoding='utf-8-sig')
                    for index, row in csv_reader.iterrows():
                        ligne_filtered = {key: value for key, value in row.items() if key in db_column_mapping.keys()}
                        cursor_destination = conn.cursor()
                        cursor_destination.execute("SELECT COUNT(*) FROM Student WHERE (NAME = ? AND SURNAME = ?) OR EMAIL = ?;", (ligne_filtered["Nom"], ligne_filtered["Prénom"], ligne_filtered["mail"]))
                        count = cursor_destination.fetchone()[0]
                        if count == 0:
                            print(f"{ligne_filtered['Nom']} {ligne_filtered['Prénom']} doesn't exist")
                        else:
                            cursor_destination.execute("UPDATE Student SET LV2=?, STATUS=? WHERE (NAME = ? AND SURNAME = ?) OR EMAIL = ? ;", (ligne_filtered["Langues"],"PRESENT", ligne_filtered["Nom"], ligne_filtered["Prénom"], ligne_filtered["mail"]))
                        conn.commit()

            elif file.endswith('.json'):
                json_file_path = os.path.join(depot_info_folder, file)
                with open(json_file_path, 'r', encoding='utf-8-sig') as json_file:
                    data = json.load(json_file)
                    for ligne in data:
                        ligne_filtered = {key: value for key, value in ligne.items() if key in db_column_mapping.keys()}
                        cursor_destination = conn.cursor()
                        cursor_destination.execute("SELECT COUNT(*) FROM Student WHERE (NAME = ? AND SURNAME = ?) OR EMAIL = ?;", (ligne_filtered["Nom"], ligne_filtered["Prénom"], ligne_filtered["mail"]))
                        count = cursor_destination.fetchone()[0]
                        if count == 0:
                            print(f"{ligne_filtered['Nom']} {ligne_filtered['Prénom']} doesn't exist")
                        else:
                            cursor_destination.execute("UPDATE Student SET LV2=?, STATUS=? WHERE (NAME = ? AND SURNAME = ?) OR EMAIL = ? ;", (ligne_filtered["Langues"],"PRESENT", ligne_filtered["Nom"], ligne_filtered["Prénom"], ligne_filtered["mail"]))
                        conn.commit()

            elif file.endswith('.xlsx'):
                xlsx_file_path = os.path.join(depot_info_folder, file)
                df = pd.read_excel(xlsx_file_path, header=0, usecols=["Nom", "Prénom", "mail", "Langues"])                
                df = df[list(db_column_mapping.keys())]
                cursor_destination = conn.cursor()
                for index, ligne in df.iterrows():
                    cursor_destination.execute("SELECT COUNT(*) FROM Student WHERE (NAME = ? AND SURNAME = ?) OR EMAIL = ?;", (ligne["Nom"], ligne["Prénom"], ligne["mail"]))
                    count = cursor_destination.fetchone()[0]
                    if count == 0:
                        #print(f"{ligne['Nom']} {ligne['Prénom']} doesn't exist")
                        pass
                    else:
                        cursor_destination.execute("UPDATE Student SET LV2=?, STATUS=? WHERE (NAME = ? AND SURNAME = ?) OR EMAIL = ? ;", (ligne["Langues"],"PRESENT", ligne["Nom"], ligne["Prénom"], ligne["mail"]))
                conn.commit()

            else:
                print(f"Format de fichier non pris en charge: {file}")

    conn.close()
    return

file_data_Student(depot_info_folder,Data)


def load_survey(depot_note_folder,db_path ):
    conn = sqlite3.connect(db_path)

    for file in [f for f in os.listdir(depot_note_folder)]:

        if "Anglais" not in os.path.splitext(os.path.basename(file))[0] :
            db_column_mapping = {
                    'Nom': 'NAME',
                    'Prénom': 'SURNAME',
                    'Mail': 'EMAIL',
                    'Note/10' : 'GRADE_LV2'
                    }

            if file.endswith('.csv'):
                csv_file_path = os.path.join(depot_note_folder, file)
                with open(csv_file_path, 'r', encoding='utf-8-sig') as csvfile:
                    csv_reader = pd.read_csv(csv_file_path, encoding='utf-8-sig')
                    csv_reader['Note/10'] = csv_reader['Note/10'].replace('', np.nan)
                    csv_reader['Note/10'] = csv_reader['Note/10'].astype(float)
                    for index, row in csv_reader.iterrows():
                        ligne_filtered = {key: value for key, value in row.items() if key in db_column_mapping.keys()}
                        cursor_destination = conn.cursor()
                        cursor_destination.execute("SELECT COUNT(*) FROM Student WHERE (NAME = ? AND SURNAME = ?) OR EMAIL = ?;", (ligne_filtered["Nom"], ligne_filtered["Prénom"], ligne_filtered["Mail"]))                    
                        count = cursor_destination.fetchone()[0]
                        if count == 0:
                            print(f"{ligne_filtered['Nom']} {ligne_filtered['Prénom']} doesn't exist")
                        else:
                            cursor_destination.execute("UPDATE Student SET GRADE_LV2=? WHERE (NAME = ? AND SURNAME = ?) OR EMAIL = ? ;", (ligne_filtered["Note/10"], ligne_filtered["Nom"], ligne_filtered["Prénom"], ligne_filtered["Mail"]))
                        conn.commit()
                            
            elif file.endswith('.json'):
                json_file_path = os.path.join(depot_note_folder, file)
                with open(json_file_path, 'r', encoding='utf-8-sig') as jsonfile:
                    data = json.load(jsonfile)
                    df = pd.DataFrame(data)
                    df['Note/10'] = df['Note/10'].replace('', np.nan).astype(float)
                    for index, row in df.iterrows():
                        ligne_filtered = {db_column_mapping[key]: row[key] for key in row.keys() if key in db_column_mapping.keys()}
                        cursor_destination = conn.cursor()
                        cursor_destination.execute("SELECT COUNT(*) FROM Student WHERE (NAME = ? AND SURNAME = ?) OR EMAIL = ?;",(ligne_filtered["NAME"], ligne_filtered["SURNAME"], ligne_filtered["EMAIL"]))
                        count = cursor_destination.fetchone()[0]
                        if count == 0:
                            print(f"{ligne_filtered['NAME']} {ligne_filtered['SURNAME']} doesn't exist")
                        else:
                            cursor_destination.execute("UPDATE Student SET GRADE_LV2=? WHERE (NAME = ? AND SURNAME = ?) OR EMAIL = ? ;", (ligne_filtered["GRADE_LV2"], ligne_filtered["NAME"], ligne_filtered["SURNAME"], ligne_filtered["EMAIL"]))
                        conn.commit()

            elif file.endswith('.xlsx'):
                xlsx_file_path = os.path.join(depot_note_folder, file)
                df = pd.read_excel(xlsx_file_path, header=0, usecols=["Nom", "Prénom", "Mail", "Note/10"])
                df['Note/10'] = df['Note/10'].replace('', np.nan).astype(float)
                for index, row in df.iterrows():
                    ligne_filtered = {db_column_mapping[key]: row[key] for key in row.keys() if key in db_column_mapping.keys()}
                    cursor_destination = conn.cursor()
                    cursor_destination.execute("SELECT COUNT(*) FROM Student WHERE (NAME = ? AND SURNAME = ?) OR EMAIL = ?;", (ligne_filtered["NAME"], ligne_filtered["SURNAME"], ligne_filtered["EMAIL"]))
                    count = cursor_destination.fetchone()[0]
                    if count == 0:
                        print(f"{ligne_filtered['NAME']} {ligne_filtered['SURNAME']} doesn't exist")
                    else:
                        cursor_destination.execute("UPDATE Student SET GRADE_LV2=? WHERE (NAME = ? AND SURNAME = ?) OR EMAIL = ? ;", (ligne_filtered["GRADE_LV2"], ligne_filtered["NAME"], ligne_filtered["SURNAME"], ligne_filtered["EMAIL"]))
                    conn.commit()
                    
            else:
                print(f"Format de fichier non pris en charge: {file}")
        
        else :
            db_column_mapping = {
                'Nom': 'NAME',
                'Prénom': 'SURNAME',
                'Mail': 'EMAIL',
                'Note/10' : 'GRADE_LV1'
            }
            if "_TT" in os.path.splitext(os.path.basename(file))[0]: 
                language = os.path.splitext(os.path.basename(file))[0]
                language = language[:-3]
                extra_time = True
                if file.endswith('.csv'):
                    csv_file_path = os.path.join(depot_note_folder, file)
                    with open(csv_file_path, 'r', encoding='utf-8-sig') as csvfile:
                        csv_reader = pd.read_csv(csv_file_path, encoding='utf-8-sig')
                        csv_reader['Note/10'] = csv_reader['Note/10'].replace('', np.nan)
                        csv_reader['Note/10'] = csv_reader['Note/10'].astype(float)
                        for index, row in csv_reader.iterrows():
                            ligne_filtered = {key: value for key, value in row.items() if key in db_column_mapping.keys()}
                            cursor_destination = conn.cursor()
                            cursor_destination.execute("SELECT COUNT(*) FROM Student WHERE (NAME = ? AND SURNAME = ?) OR EMAIL = ?;", (ligne_filtered["Nom"], ligne_filtered["Prénom"], ligne_filtered["Mail"]))                    
                            count = cursor_destination.fetchone()[0]
                            if count == 0:
                                print(f"{ligne_filtered['Nom']} {ligne_filtered['Prénom']} doesn't exist")
                            else:
                                cursor_destination.execute("UPDATE Student SET GRADE_LV1=?, LV1=?, EXTRA_TIME=? WHERE (NAME = ? AND SURNAME = ?) OR EMAIL = ? ;", (ligne_filtered["Note/10"], language, extra_time, ligne_filtered["Nom"], ligne_filtered["Prénom"], ligne_filtered["Mail"]))
                            conn.commit()

                elif file.endswith('.json'):
                    json_file_path = os.path.join(depot_note_folder, file)
                    with open(json_file_path, 'r', encoding='utf-8-sig') as jsonfile:
                        data = json.load(jsonfile)
                        df = pd.DataFrame(data)
                        df['Note/10'] = df['Note/10'].replace('', np.nan).astype(float)
                        for index, row in df.iterrows():
                            ligne_filtered = {db_column_mapping[key]: row[key] for key in row.keys() if key in db_column_mapping.keys()}
                            cursor_destination = conn.cursor()
                            cursor_destination.execute("SELECT COUNT(*) FROM Student WHERE (NAME = ? AND SURNAME = ?) OR EMAIL = ?;",(ligne_filtered["NAME"], ligne_filtered["SURNAME"], ligne_filtered["EMAIL"]))
                            count = cursor_destination.fetchone()[0]
                            if count == 0:
                                print(f"{ligne_filtered['NAME']} {ligne_filtered['SURNAME']} doesn't exist")
                            else:
                                cursor_destination.execute("UPDATE Student SET GRADE_LV1=?, LV1=?, EXTRA_TIME=? WHERE (NAME = ? AND SURNAME = ?) OR EMAIL = ? ;", (ligne_filtered["GRADE_LV1"], language, extra_time, ligne_filtered["NAME"], ligne_filtered["SURNAME"], ligne_filtered["EMAIL"]))
                            conn.commit()

                elif file.endswith('.xlsx'):
                    xlsx_file_path = os.path.join(depot_note_folder, file)
                    df = pd.read_excel(xlsx_file_path, header=0, usecols=["Nom", "Prénom", "Mail", "Note/10"])
                    df['Note/10'] = df['Note/10'].replace('', np.nan).astype(float)
                    for index, row in df.iterrows():
                        ligne_filtered = {db_column_mapping[key]: row[key] for key in row.keys() if key in db_column_mapping.keys()}
                        cursor_destination = conn.cursor()
                        cursor_destination.execute("SELECT COUNT(*) FROM Student WHERE (NAME = ? AND SURNAME = ?) OR EMAIL = ?;", (ligne_filtered["NAME"], ligne_filtered["SURNAME"], ligne_filtered["EMAIL"]))
                        count = cursor_destination.fetchone()[0]
                        if count == 0:
                            print(f"{ligne_filtered['NAME']} {ligne_filtered['SURNAME']} doesn't exist")
                        else:
                            cursor_destination.execute("UPDATE Student SET GRADE_LV1=?, LV1=?, EXTRA_TIME=? WHERE (NAME = ? AND SURNAME = ?) OR EMAIL = ? ;", (ligne_filtered["GRADE_LV1"], language, extra_time, ligne_filtered["NAME"], ligne_filtered["SURNAME"], ligne_filtered["EMAIL"]))
                        conn.commit()
                else:
                    print(f"Format de fichier non pris en charge: {file}")
                
            else :
                extra_time = False
                if file.endswith('.csv'):
                    csv_file_path = os.path.join(depot_note_folder, file)
                    with open(csv_file_path, 'r', encoding='utf-8-sig') as csvfile:
                        csv_reader = pd.read_csv(csv_file_path, encoding='utf-8-sig')
                        csv_reader['Note/10'] = csv_reader['Note/10'].replace('', np.nan)
                        csv_reader['Note/10'] = csv_reader['Note/10'].astype(float)
                        for index, row in csv_reader.iterrows():
                            ligne_filtered = {key: value for key, value in row.items() if key in db_column_mapping.keys()}
                            cursor_destination = conn.cursor()
                            cursor_destination.execute("SELECT COUNT(*) FROM Student WHERE (NAME = ? AND SURNAME = ?) OR EMAIL = ?;", (ligne_filtered["Nom"], ligne_filtered["Prénom"], ligne_filtered["Mail"]))                    
                            count = cursor_destination.fetchone()[0]
                            if count == 0:
                                print(f"{ligne_filtered['Nom']} {ligne_filtered['Prénom']} doesn't exist")
                            else:
                                cursor_destination.execute("UPDATE Student SET GRADE_LV1=?, LV1=?, EXTRA_TIME=? WHERE (NAME = ? AND SURNAME = ?) OR EMAIL = ? ;", (ligne_filtered["Note/10"], os.path.splitext(os.path.basename(file))[0], extra_time, ligne_filtered["Nom"], ligne_filtered["Prénom"], ligne_filtered["Mail"]))
                            conn.commit()
                            
                elif file.endswith('.json'):
                    json_file_path = os.path.join(depot_note_folder, file)
                    with open(json_file_path, 'r', encoding='utf-8-sig') as jsonfile:
                        data = json.load(jsonfile)
                        df = pd.DataFrame(data)
                        df['Note/10'] = df['Note/10'].replace('', np.nan).astype(float)
                        for index, row in df.iterrows():
                            ligne_filtered = {db_column_mapping[key]: row[key] for key in row.keys() if key in db_column_mapping.keys()}
                            cursor_destination = conn.cursor()
                            cursor_destination.execute("SELECT COUNT(*) FROM Student WHERE (NAME = ? AND SURNAME = ?) OR EMAIL = ?;",(ligne_filtered["NAME"], ligne_filtered["SURNAME"], ligne_filtered["EMAIL"]))
                            count = cursor_destination.fetchone()[0]
                            if count == 0:
                                print(f"{ligne_filtered['NAME']} {ligne_filtered['SURNAME']} doesn't exist")
                            else:
                                cursor_destination.execute("UPDATE Student SET GRADE_LV1=?, LV1=?, EXTRA_TIME=? WHERE (NAME = ? AND SURNAME = ?) OR EMAIL = ? ;", (ligne_filtered["GRADE_LV1"], os.path.splitext(os.path.basename(file))[0], extra_time, ligne_filtered["NAME"], ligne_filtered["SURNAME"], ligne_filtered["EMAIL"]))
                            conn.commit()

                elif file.endswith('.xlsx'):
                    xlsx_file_path = os.path.join(depot_note_folder, file)
                    df = pd.read_excel(xlsx_file_path, header=0, usecols=["Nom", "Prénom", "Mail", "Note/10"])
                    df['Note/10'] = df['Note/10'].replace('', np.nan).astype(float)
                    for index, row in df.iterrows():
                        ligne_filtered = {db_column_mapping[key]: row[key] for key in row.keys() if key in db_column_mapping.keys()}
                        cursor_destination = conn.cursor()
                        cursor_destination.execute("SELECT COUNT(*) FROM Student WHERE (NAME = ? AND SURNAME = ?) OR EMAIL = ?;", (ligne_filtered["NAME"], ligne_filtered["SURNAME"], ligne_filtered["EMAIL"]))
                        count = cursor_destination.fetchone()[0]
                        if count == 0:
                            print(f"{ligne_filtered['NAME']} {ligne_filtered['SURNAME']} doesn't exist")
                        else:
                                cursor_destination.execute("UPDATE Student SET GRADE_LV1=?, LV1=?, EXTRA_TIME=? WHERE (NAME = ? AND SURNAME = ?) OR EMAIL = ? ;", (ligne_filtered["GRADE_LV1"], os.path.splitext(os.path.basename(file))[0], extra_time, ligne_filtered["NAME"], ligne_filtered["SURNAME"], ligne_filtered["EMAIL"]))
                        conn.commit()
                else:
                    print(f"Format de fichier non pris en charge: {file}")

    conn.close()
    return


load_survey(depot_note_folder,Data)


def find_list_CLASS(Data):
    conn = sqlite3.connect(Data)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT(CLASS) FROM Student;")
    list_Class = cursor.fetchall()
    list_Class = [row[0] for row in list_Class]
    conn.close()
    return list_Class


def find_list_LV2(Data, Class):
    conn = sqlite3.connect(Data)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT(LV2) FROM Student WHERE Class = '" + Class + "';")
    list_lv2 = cursor.fetchall()
    list_lv2 = [row[0] for row in list_lv2]
    conn.close()
    return list_lv2

def find_list_LV1(Data):
    conn = sqlite3.connect(Data)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT(LV1) FROM Student;")
    list_lv1 = cursor.fetchall()
    list_lv1 = [row[0] for row in list_lv1]
    conn.close()
    return list_lv1

def nomber_class(nomber_student, nomber_by_class):
    nomber_class = 0
    # à expliquer 
    if (nomber_student % nomber_by_class) > ((nomber_student //nomber_by_class)*(2/3)) :
        nomber_class = nomber_student//nomber_by_class + 1
    else :
        nomber_class = nomber_student//nomber_by_class
    
    if  nomber_class == 0:
        nomber_class = 1
    return nomber_class



def make_groups(list_student, number_class):
    total_students = len(list_student)
    if total_students !=0:
        students_per_group = total_students // number_class
        extra_students = total_students % number_class
        # Nombre d'étudiants supplémentaires par groupe
        extra_per_group = [1 if i < extra_students else 0 for i in range(number_class)]
        groups = []
        start_idx = 0
        for i in range(number_class):
            # Nombre d'étudiants dans ce groupe
            group_size = students_per_group + extra_per_group[i]
            end_idx = start_idx + group_size
            groups.append(list_student[start_idx:end_idx])
            start_idx = end_idx
        return groups


def made_LV2_groupe(Data,nb_forecast_by_class, nb_by_class):
    for name_class in find_list_CLASS(Data):
        nb_forecast = nb_forecast_by_class[name_class]
        if nb_forecast== 0:
            for name_lv2 in find_list_LV2(Data, name_class):
                if "-débutant (jamais étudié)" in name_lv2 :
                    conn = sqlite3.connect(Data)
                    cursor = conn.cursor()
                    cursor.execute("SELECT EMAIL FROM Student WHERE CLASS='" + name_class + "'AND LV2='" + name_lv2 + "';")
                    group = cursor.fetchall()
                    group = [pos[0] for pos in group]
                    nb_class = nomber_class(len(group),nb_by_class)
                    groups = make_groups(group, nb_class)
                    i = 1
                    for group in groups:
                        name_group = 'G' +str(i)        #donner un nom plus explicite
                        conn = sqlite3.connect(Data)
                        cursor = conn.cursor()
                        cursor.execute("INSERT INTO Groups(CLASS, LV, GROUP_LV) VALUES(?,?,?);", (name_class, name_lv2, name_group))
                        for student in group:
                            cursor.execute("UPDATE Student SET GROUP_LV2=? WHERE EMAIL=?;", (name_group, student))
                            conn.commit()  
                            cursor.fetchall()  
                        i+=1
                else : 
                    conn = sqlite3.connect(Data)
                    cursor = conn.cursor()
                    cursor.execute("SELECT EMAIL,GRADE_LV2 FROM Student WHERE CLASS='" + name_class + "'AND LV2='" + name_lv2 + "' ORDER BY GRADE_LV2 DESC;")
                    group = cursor.fetchall()
                    nb_class = nomber_class(len(group),nb_by_class)
                    groups = make_groups(group, nb_class)
                    i = 1
                    for group in groups:
                        name_group = 'G' +str(i)        #donner un nom plus explicite
                        conn = sqlite3.connect(Data)
                        cursor = conn.cursor()
                        cursor.execute("INSERT INTO Groups(CLASS, LV, GROUP_LV) VALUES(?,?,?);", (name_class, name_lv2, name_group))
                        for student in group:
                            cursor.execute("UPDATE Student SET GROUP_LV2=? WHERE EMAIL=?;", (name_group, student[0]))
                            conn.commit()  
                            cursor.fetchall()  
                        i+=1  
            conn.close()                                                           
        else :
            conn = sqlite3.connect(Data)
            for name_lv2 in find_list_LV2(Data, name_class):
                cursor = conn.cursor()
                cursor.execute("SELECT count(*) FROM Student WHERE CLASS='" + name_class + "';")
                total = cursor.fetchone()[0]  
                cursor.execute("SELECT count(*) FROM Student WHERE CLASS='" + name_class + "' AND LV2='" + name_lv2 + "';")
                group = cursor.fetchone()[0]  
                if total != 0:
                    ratio = group / total * nb_forecast_by_class[name_class]
                    rounded_ratio = round(ratio) 
                if "-débutant (jamais étudié)" in name_lv2 :
                    cursor.execute("SELECT EMAIL FROM Student WHERE CLASS='" + name_class + "'AND LV2='" + name_lv2 + "';")
                    group = cursor.fetchall()
                    group = [pos[0] for pos in group]
                    for i in range(rounded_ratio):
                        group.append('forecast')
                    nb_class = nomber_class(len(group),nb_by_class)
                    groups = make_groups(group, nb_class)
                    i = 1
                    for group in groups:
                        name_group = 'G' +str(i)        #donner un nom plus explicite
                        conn = sqlite3.connect(Data)
                        cursor = conn.cursor()
                        cursor.execute("INSERT INTO Groups(CLASS, LV, GROUP_LV) VALUES(?,?,?);", (name_class, name_lv2, name_group))
                        for student in group:
                            if student !='forecast':
                                cursor.execute("UPDATE Student SET GROUP_LV2=? WHERE EMAIL=?;", (name_group, student))
                                conn.commit()  
                                cursor.fetchall()  
                        i+=1
                else : 
                    cursor.execute("SELECT EMAIL,GRADE_LV2 FROM Student WHERE CLASS='" + name_class + "'AND LV2='" + name_lv2 + "' ORDER BY GRADE_LV2 DESC;")
                    group = cursor.fetchall()
                    numeric_values = [valeur for _, valeur in group if isinstance(valeur, (int, float))]
                    mu = np.mean(numeric_values)
                    sigma = np.var(numeric_values)**0.5
                    for i in range(rounded_ratio):
                        valeur_gaussienne = str(np.random.normal(mu, sigma))
                        group.append(('forecast',float(valeur_gaussienne)))
                    group = sorted(group, key=lambda x: x[1])
                    nb_class = nomber_class(len(group),nb_by_class)
                    groups = make_groups(group, nb_class)
                    i = 1
                    for group in groups:
                        name_group = 'G' +str(i)        #donner un nom plus explicite
                        cursor = conn.cursor()
                        cursor.execute("INSERT INTO Groups(CLASS, LV, GROUP_LV) VALUES(?,?,?);", (name_class, name_lv2, name_group))
                        for student in group:
                            if student !='forecast':
                                cursor.execute("UPDATE Student SET GROUP_LV2=? WHERE EMAIL=?;", (name_group, student[0]))
                                conn.commit()  
                                cursor.fetchall()  
                        i+=1
            conn.close()
    return 



made_LV2_groupe(Data,nb_forecast_by_class, nb_by_class)



def made_LV1_groupe(Data,nb_forecast_by_class, nb_by_class):
    for name_class in find_list_CLASS(Data):
        nb_forecast = nb_forecast_by_class[name_class]
        if nb_forecast== 0:
            conn = sqlite3.connect(Data)            
            for name_lv1 in find_list_LV1(Data):
                cursor = conn.cursor()
                cursor.execute("SELECT EMAIL,GRADE_LV1 FROM Student WHERE CLASS='" + name_class + "'AND LV1='" + name_lv1 + "' ORDER BY GRADE_LV1 DESC;")
                group = cursor.fetchall()
                nb_class = nomber_class(len(group),nb_by_class)
                print(nb_class)
                groups = make_groups(group, nb_class)
                i = 1
                for group in groups:
                    name_group = 'G' +str(i)        #donner un nom plus explicite
                    conn = sqlite3.connect(Data)
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO Groups(CLASS, LV, GROUP_LV) VALUES(?,?,?);", (name_class, name_lv1, name_group))
                    for student in group:
                        cursor.execute("UPDATE Student SET GROUP_LV1=? WHERE EMAIL=?;", (name_group, student[0]))
                        conn.commit()  
                        cursor.fetchall()  
                    i+=1  
            conn.close()                                                           
        else :
            conn = sqlite3.connect(Data)
            for name_lv1 in find_list_LV1(Data):
                cursor = conn.cursor()
                cursor.execute("SELECT count(*) FROM Student WHERE CLASS='" + name_class + "';")
                total = cursor.fetchone()[0]  
                cursor.execute("SELECT count(*) FROM Student WHERE CLASS='" + name_class + "' AND LV1='" + name_lv1 + "';")
                group = cursor.fetchone()[0]  
                if total != 0:
                    ratio = group / total * nb_forecast_by_class[name_class]
                    rounded_ratio = round(ratio)  
                cursor.execute("SELECT EMAIL,GRADE_LV1 FROM Student WHERE CLASS='" + name_class + "'AND LV1='" + name_lv1 + "' ORDER BY GRADE_LV1 DESC;")
                group = cursor.fetchall()
                numeric_values = [valeur for _, valeur in group if isinstance(valeur, (int, float))]
                mu = np.mean(numeric_values)
                sigma = np.var(numeric_values)**0.5
                for i in range(rounded_ratio):
                    valeur_gaussienne = str(np.random.normal(mu, sigma))
                    group.append(('forecast',float(valeur_gaussienne)))
                group = sorted(group, key=lambda x: x[1])
                nb_class = nomber_class(len(group),nb_by_class)
                groups = make_groups(group, nb_class)
                i = 1
                for group in groups:
                    name_group = 'G' +str(i)        #donner un nom plus explicite
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO Groups(CLASS, LV, GROUP_LV) VALUES(?,?,?);", (name_class, name_lv1, name_group))
                    for student in group:
                        if student !='forecast':
                            cursor.execute("UPDATE Student SET GROUP_LV1=? WHERE EMAIL=?;", (name_group, student[0]))
                            conn.commit()  
                            cursor.fetchall()  
                    i+=1
            conn.close()
    return



made_LV1_groupe(Data,nb_forecast_by_class, nb_by_class)


def Delete_data_table(filename, table):
    conn = sqlite3.connect(filename)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM '" + table + "';")
    conn.commit() 
    tables = cursor.fetchall()
    conn.close()
    return 

Delete_data_table(Data, "Availabilities")



def Set_Availabilities(Data, DAYS, nb_H_per_day):
    conn = sqlite3.connect(Data)
    cursor = conn.cursor()
    for i in DAYS :
        for j in range (nb_H_per_day):
            hour = "slot" + str(j+1)
            ID = str(i[:3]) +  "_" + str(hour)
            cursor.execute("INSERT INTO Availabilities VALUES (?,?,?);",(ID,i, hour ))
    conn.commit() 
    conn.close()
    return 

Set_Availabilities(Data, DAYS, nb_slot)


def Delete_data_table(filename, table):
    conn = sqlite3.connect(filename)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM '" + table + "';")
    conn.commit() 
    tables = cursor.fetchall()
    conn.close()
    return 

Delete_data_table(Data, "Rooms")

def Set_Rooms(Data, Rooms):
    conn = sqlite3.connect(Data)
    cursor = conn.cursor()
    for i in Rooms :
        ID = i
        cursor.execute("INSERT INTO Rooms VALUES (?,?);",(ID,i))
    conn.commit() 
    conn.close()
    return 

Set_Rooms(Data, Rooms)


def Set_Rooms(Data, list_teacher):
    conn = sqlite3.connect(Data)
    cursor = conn.cursor()

    teacher_emails = [teacher[2] for teacher in list_teacher]
    cursor.execute("DELETE FROM Teachers WHERE EMAIL NOT IN (" + ",".join(["?"] * len(teacher_emails)) + ")", teacher_emails)

    for i in list_teacher :
        cursor.execute("SELECT count(*) FROM Teachers WHERE  NAME=? AND SURNAME=? AND EMAIL = ? AND SUBJECT = ?", (i[0],i[1],i[2],i[3]))
        presence = cursor.fetchall()
        if presence[0][0] == 0  :
            ID = i[0][:3] + "_" + i[3][:3]
            cursor.execute("INSERT INTO Teachers VALUES (?,?,?,?,?);", (ID,i[0],i[1],i[2],i[3]))

    conn.commit() 
    conn.close()
    return 

Set_Rooms(Data, list_teacher)


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
cursor.execute("SELECT DISTINCT(CLASS) FROM Student;")
list_ID_Class = cursor.fetchall()
list_ID_Class = [row[0] for row in list_ID_Class]
conn.close()


def create_random_pairs(list1, list2, num_pairs):
    pairs = []
    for item1 in list1:
        selected_items = random.sample(list2, num_pairs)
        for item2 in selected_items:
            pairs.append((item1, item2))

    return pairs


list_availibity_teachers = create_random_pairs(list_ID_Teacher, list_ID_Availability,3)
list_availibity_rooms = create_random_pairs(list_ID_room, list_ID_Availability,6)
list_availibity_class = create_random_pairs(list_ID_Class,list_ID_Availability, 6)

def Set_table_de_jointure(Data, table, list_availibity_rooms):
    conn = sqlite3.connect(Data)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM '" + table + "';")
    for i in list_availibity_rooms :
        cursor.execute("INSERT INTO '" + table + "' VALUES (?,?);",(i[0],i[1]))
    conn.commit() 
    conn.close()

Set_table_de_jointure(Data, 'Availability_Rooms' ,list_availibity_rooms)
Set_table_de_jointure(Data, 'Availability_Teachers' ,list_availibity_teachers)
Set_table_de_jointure(Data, 'Availability_Class', list_availibity_class)




from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER


def pdf_maker(group, langage, Class, list_student):
    styles = getSampleStyleSheet()  

    pdf_path = f"data/output_pdf/{Class}-{langage}_{group}.pdf"
    if os.path.exists(pdf_path):
        os.remove(pdf_path)

    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    content = []

    title = Paragraph(f"<b>{Class} : {langage}_{group}</b>", styles["Title"])
    content.append(title)
    content.append(Spacer(1, 12))  

    data = list_student
    table_data = [("Name", "Surname", "Email", "Mark", "Extra_time")]
    table_data.extend(data)  


    table = Table(table_data)
    style = TableStyle([('BACKGROUND', (0,0), (-1,0), colors.grey),
                        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                        ('BOTTOMPADDING', (0,0), (-1,0), 12),
                        ('BACKGROUND', (0,1), (-1,-1), colors.beige),
                        ('GRID', (0,0), (-1,-1), 1, colors.black)])
    table.setStyle(style)

    content.append(table)

    content.append(Spacer(1, 12)) 
    centered_style = ParagraphStyle(name='Centered', parent=styles['Normal'], alignment=TA_CENTER)
    
    if "-débutant" not in langage: 
        marks = [member[3] for member in list_student] 
        mean_mark = sum(marks) / len(marks) if marks else 0
        summary = Paragraph(f"Number of student: {len(list_student)} ; Mark mean: {mean_mark:.2f}", centered_style)
    else :
        mean_mark = "BEGINNER"
        summary = Paragraph(f"Number of student: {len(list_student)} ; Mark mean: {mean_mark}", centered_style)
    
    content.append(summary)

    content.append(Spacer(1, 40)) 

    list_mail = ', '.join([tuple_[2] for tuple_ in data])
    email_paragraph = Paragraph(f"<b>Emails:</b> {list_mail}", styles["Normal"])
    content.append(email_paragraph)

    doc.build(content)
    #print(f"Le fichier PDF '{pdf_path}' a été créé avec succès.")  {mean_mark:.2f}


def clear_output_pdf(folder):
    for nom_fichier in os.listdir(folder):
        chemin_fichier = os.path.join(folder, nom_fichier)
        if os.path.isfile(chemin_fichier):
            os.remove(chemin_fichier)

folder_to_clear = "data/output_pdf"
clear_output_pdf(folder_to_clear)

def made_LV1_PDF(Data):
    for name_class in find_list_CLASS(Data):
        for name_lv1 in find_list_LV1(Data):
            conn = sqlite3.connect(Data)
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT(GROUP_LV1) FROM Student WHERE CLASS='" + name_class + "'AND LV1='" + name_lv1 + "';")
            list_group = cursor.fetchall()
            list_group = [row[0] for row in list_group]
            for num_group in list_group :
                cursor = conn.cursor()
                cursor.execute("SELECT NAME,SURNAME, EMAIL, GRADE_LV1, EXTRA_TIME FROM Student WHERE CLASS='" + name_class + "'AND GROUP_LV1= '" + num_group + "'AND  LV1='" + name_lv1 + "';")
                group = cursor.fetchall() 
                group_modify = [tuple_[:4] + ('YES' if tuple_[4] == 1 else 'NO',) for tuple_ in group]
                pdf_maker(num_group, name_lv1, name_class, group_modify)
    conn.close()

def made_LV2_PDF(Data):
    for name_class in find_list_CLASS(Data):
        for name_lv2 in find_list_LV2(Data, name_class):
            conn = sqlite3.connect(Data)
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT(GROUP_LV2) FROM Student WHERE CLASS='" + name_class + "'AND LV2='" + name_lv2 + "';")
            list_group = cursor.fetchall()
            list_group = [row[0] for row in list_group]
            for num_group in list_group :
                cursor = conn.cursor()
                cursor.execute("SELECT NAME,SURNAME, EMAIL, GRADE_LV2, EXTRA_TIME FROM Student WHERE CLASS='" + name_class + "'AND GROUP_LV2= '" + num_group + "'AND  LV2='" + name_lv2 + "';")
                group = cursor.fetchall() 
                group_modify = [tuple_[:4] + ('YES' if tuple_[4] == 1 else 'NO',) for tuple_ in group]
                pdf_maker(num_group, name_lv2, name_class, group_modify)
    conn.close()

made_LV1_PDF(Data)
made_LV2_PDF(Data)
