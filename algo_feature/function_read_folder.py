import pandas as pd
import json
import os
import numpy as np
import sqlite3

def load_teachers(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    list_teacher = []
    list_availability_teachers = []

    # Mapping for subject names and abbreviations for availability codes
    subject_mapping = {
        'English': 'ANGLAIS',
        'Spanish': 'ESPAGNOL',
        'German': 'ALLEMAND',
        'Chinese': 'CHINOIS'
    }

    day_slot_mapping = {
        'Monday Morning': 'Mon_1',
        'Monday Afternoon': 'Mon_2',
        'Monday Evening': 'Mon_3',
        'Tuesday Morning': 'Tue_1',
        'Tuesday Afternoon': 'Tue_2',
        'Tuesday Evening': 'Tue_3',
        'Wednesday Morning': 'Wed_1',
        'Wednesday Afternoon': 'Wed_2',
        'Wednesday Evening': 'Wed_3',
        'Thursday Morning': 'Thu_1',
        'Thursday Afternoon': 'Thu_2',
        'Thursday Evening': 'Thu_3',
        'Friday Morning': 'Fri_1',
        'Friday Afternoon': 'Fri_2',
        'Friday Evening': 'Fri_3'
    }

    for teacher in data:
        name_parts = teacher['name'].upper().split()
        FIRSTNAME_parts = teacher['FIRSTNAME'].upper().split()
        email = teacher['email']
        subject = subject_mapping.get(teacher['subject'], teacher['subject'])

        teacher_tuple = (name_parts[0], FIRSTNAME_parts[0], email, subject)
        list_teacher.append(teacher_tuple)

        # Generate the teacher's availability code
        teacher_code = f"{FIRSTNAME_parts[0][:3]}_{subject[:3].upper()}"

        for availability in teacher['availabilities']:
            availability_code = day_slot_mapping.get(availability, availability)
            list_availability_teachers.append((teacher_code, availability_code))

    return list_teacher, list_availability_teachers

def file_data_Student(depot_info_folder): 
    for file in [f for f in os.listdir(depot_info_folder)]:
        if os.path.splitext(os.path.basename(file))[0] == 'Student_Info' :
            db_column_mapping = {
                'Nom': 'NAME',
                'Prénom': 'FIRSTNAME',
                'Mail': 'EMAIL',
                'Programme': 'SCHOOL_YEAR'}
        elif os.path.splitext(os.path.basename(file))[0] == 'Student_Sondage_LV2' :
            file_path = os.path.join(depot_info_folder, file)
            db_column_mapping = {
                'Nom': 'NAME',
                'Prénom': 'FIRSTNAME',
                'Mail': 'EMAIL',
                'Langues' : 'LV2'
            }
            
        else:
            print(f"Format de fichier non pris en charge: {file}")
            continue
    
        file_path = os.path.join(depot_info_folder, file)
        if 'Student_Info' in file:
            if file.endswith('.csv'):
                df = csv_into_dataframe(file_path, db_column_mapping)

            elif file.endswith('.json'):
                df = json_into_dataframe(file_path, db_column_mapping)

            elif file.endswith('.xlsx'):
                df = xlsx_into_dataframe(file_path, db_column_mapping)

            else:
                print(f"Format de fichier non pris en charge: {file}")

        if 'Student_Sondage_LV2' in file:
            if file.endswith('.csv'):
                update_lv2_from_csv(df, file_path)
            elif file.endswith('.json'):
                update_lv2_from_json(df, file_path)
            elif file.endswith('.xlsx'):
                update_lv2_from_xlsx(df, file_path)
            else:
                print(f"Format de fichier non pris en charge: {file}")
    map_school_year(df, 'SCHOOL_YEAR')
    return df

def map_school_year(df, colonne):
    correspondance = {
        'PMBEE1': '1ABEE',
        'PMBEE2': '2ABEE',
        'PMBEE3': '3ABEE',
        'PMFGE1': '1AFG',
        'PMFGE2': '2AFG',
        'PMFGE3': '3AFG',
        'PMSTI1': '1AFT',
        'PMSTI2': '2AFT'
    }
    df[colonne] = df[colonne].replace(correspondance)
    return df
    
    
def clean_text(text):
    replacements = {
        '�': 'é',  # Remplacer le caractère bizarre par 'é'
        # Ajoutez d'autres remplacements si nécessaire
    }
    if isinstance(text, str):
        for bad_char, good_char in replacements.items():
            text = text.replace(bad_char, good_char)
    return text

def csv_into_dataframe(file_path, db_column_mapping):
    df = pd.read_csv(file_path, encoding='utf-8-sig')
    df = df.applymap(clean_text)    # type: ignore
    df.rename(columns=db_column_mapping, inplace=True)
    df = df[list(db_column_mapping.values())]
    return df

def json_into_dataframe(file_path, db_column_mapping):
    with open(file_path, 'r', encoding='utf-8-sig') as json_file:
        data = json.load(json_file)
        transformed_data = []
        for item in data:
            transformed_item = {db_column: item.get(json_field) for json_field, db_column in db_column_mapping.items()}
            transformed_data.append(transformed_item)
        df = pd.DataFrame(transformed_data)
    return df

def xlsx_into_dataframe(file_path, db_column_mapping):
    df = pd.read_excel(file_path)
    df.rename(columns=db_column_mapping, inplace=True)
    df = df[list(db_column_mapping.values())]
    return df


def update_lv2_from_csv(students_info, file_path):
    csv_reader = pd.read_csv(file_path, encoding='utf-8-sig')
    df = df.applymap(clean_text)
    for index, row in csv_reader.iterrows():
        if ((students_info['NAME'] == row['Nom']) & (students_info['FIRSTNAME'] == row['Prénom'])).any():
                students_info.loc[(students_info['NAME'] == row['Nom']) & (students_info['FIRSTNAME'] == row['Prénom']), 'LV2'] = row['Langues']
                
def update_lv2_from_json(students_info, file_path):
    with open(file_path, 'r', encoding='utf-8-sig') as json_file:
        data = json.load(json_file)
        for row in data:
            if ((students_info['NAME'] == row['Nom']) & (students_info['FIRSTNAME'] == row['Prénom'])).any():
                students_info.loc[(students_info['NAME'] == row['Nom']) & (students_info['FIRSTNAME'] == row['Prénom']), 'LV2'] = row['Langues']

def update_lv2_from_xlsx(students_info, file_path):
    xls_df = pd.read_excel(file_path)
    for index, row in xls_df.iterrows():
        if ((students_info['NAME'] == row['Nom']) & (students_info['FIRSTNAME'] == row['Prénom'])).any():
                students_info.loc[(students_info['NAME'] == row['Nom']) & (students_info['FIRSTNAME'] == row['Prénom']), 'LV2'] = row['Langues']
                
def update_student_grade(grade_list, students_info, LV):
    for index, row in grade_list.iterrows():
        if ((students_info['NAME'] == row['Nom']) & (students_info['FIRSTNAME'] == row['Prénom'])).any():
            students_info.loc[(students_info['NAME'] == row['Nom']) & (students_info['FIRSTNAME'] == row['Prénom']), LV] = row['Note/10,00']
        else:
            print(f"{row['Nom']} {row['Prénom']} doesn't exist")     
    return students_info

def update_students_info_csv(file_path, students_info, LV):
    with open(file_path, 'r', encoding='utf-8-sig'):
        csv_reader = pd.read_csv(file_path, encoding='utf-8-sig')
        csv_reader.columns = [clean_text(col) for col in csv_reader.columns]
        csv_reader = csv_reader.applymap(clean_text) # type: ignore
        csv_reader['Note/10,00'] = csv_reader['Note/10,00'].replace('', np.nan)
        csv_reader['Note/10,00'] = csv_reader['Note/10,00'].replace(';', '.')
        csv_reader['Note/10,00'] = csv_reader['Note/10,00'].astype(float)
    students_info = update_student_grade(csv_reader, students_info, LV)
    students_info = is_file_TT(file_path, students_info, csv_reader)
    return students_info

def update_students_info_json(file_path, students_info, LV):
    with open(file_path, 'r', encoding='utf-8-sig') as jsonfile:
        data = json.load(jsonfile)
        df = pd.DataFrame(data)
        df['Note/10,00'] = df['Note/10,00'].replace('', np.nan).astype(float)
    students_info = update_student_grade(df, students_info, LV)
    students_info = is_file_TT(file_path, students_info, df)
    return students_info

def update_students_info_xlsx(file_path, students_info, LV):
    df = pd.read_excel(file_path)
    df['Note/10,00'] = df['Note/10,00'].replace('', np.nan).astype(float)
    students_info = update_student_grade(df, students_info, LV)
    is_file_TT(file_path, students_info, df)
    return students_info

def is_file_TT(file_path, students_info, grade_list):
    if '_TT' in file_path:
        students_info = update_TT(grade_list, students_info)
    return students_info

def update_TT(grade_list, students_info):
    students_info['key'] = students_info['NAME'] + '_' + students_info['FIRSTNAME']
    grade_list['key'] = grade_list['Nom'] + '_' + grade_list['Prénom']

    existing_true_indices = students_info.loc[students_info['REDUCED_EXAM'], 'key'].index
    students_info['REDUCED_EXAM'] = students_info['key'].isin(grade_list['key']) | students_info['REDUCED_EXAM']

    #students_info.loc[existing_true_indices, 'extra_time'] = True
    students_info.loc[existing_true_indices, 'REDUCED_EXAM'] = True

    students_info.drop(['key'], axis=1, inplace=True)
    grade_list.drop(['key'], axis=1, inplace=True)
    return students_info

    
def find_format_to_update_students_info(file, depot_note_folder, students_info):
    file_path = os.path.join(depot_note_folder, file)
    #print(file)
    if 'Anglais' not in file:
        if file.endswith('.csv'):
            students_info = update_students_info_csv(file_path, students_info, 'GRADE_LV2')
            
        elif file.endswith('.json'):
            students_info = update_students_info_json(file_path, students_info, 'GRADE_LV2')
            
        elif file.endswith('.xlsx'):
            students_info = update_students_info_xlsx(file_path, students_info, 'GRADE_LV2')
            
        else:
            print(f"Format de fichier non pris en charge: {file}")
           
    elif 'Anglais' in file:
        if file.endswith('.csv'):
            students_info = update_students_info_csv(file_path, students_info, 'GRADE_LV1')
            
        elif file.endswith('.json'):
            students_info = update_students_info_json(file_path, students_info, 'GRADE_LV1')
            
        elif file.endswith('.xlsx'):
            students_info = update_students_info_xlsx(file_path, students_info, 'GRADE_LV1')
            
        else:
            print(f"Format de fichier non pris en charge: {file}")


def add_student_grade(depot_note_folder, students_info):
    students_info['REDUCED_EXAM'] = False
    for file in [f for f in os.listdir(depot_note_folder)]:
        find_format_to_update_students_info(file, depot_note_folder, students_info)
    #remplit la colonne statut (présent pour tout le monde) et la colonne LV1
    students_info.insert(loc=5, column='STATUS', value='PRESENT')
    students_info.insert(loc=7, column='LV1', value='ANGLAIS')
    students_info['GRADE_LV2'] = students_info['GRADE_LV2'].fillna(0)
    return students_info