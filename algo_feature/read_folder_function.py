##################################################################################
#                        Teacher and Student Information Module                  #
##################################################################################
# Provides functionalities to manage and process information related to teachers #
# and students. It includes loading teacher data from JSON files, processing     #
# student information from various file formats, and updating student grades.    #
##################################################################################

# --------------------------------------------------------------------------------
# Modules:
# --------------------------------------------------------------------------------
# 1. load_teachers:
#    - Loads teacher information from a JSON file and transforms it into lists of 
#      teachers and their availabilities.
#
# 2. file_data_Student:
#    - Processes student information from various file formats and creates a dataframe.
#
# 3. map_school_year:
#    - Maps school year values in the dataframe.
#
# 4. clean_text:
#    - Cleans text by replacing specific unwanted characters.
#
# 5. csv_into_dataframe:
#    - Converts data from a CSV file into a DataFrame.
#
# 6. json_into_dataframe:
#    - Converts data from a JSON file into a DataFrame.
#
# 7. xlsx_into_dataframe:
#    - Converts data from an XLSX file into a DataFrame.
#
# 8. update_lv2_from_csv:
#    - Updates student second language (LV2) data from a CSV file.
#
# 9. update_lv2_from_json:
#    - Updates student second language (LV2) data from a JSON file.
#
# 10. update_lv2_from_xlsx:
#     - Updates student second language (LV2) data from an XLSX file.
#
# 11. update_student_grade:
#     - Updates student grades in the dataframe.
#
# 12. update_students_info_csv:
#     - Updates student information from a CSV grade file.
#
# 13. update_students_info_json:
#     - Updates student information from a JSON grade file.
#
# 14. update_students_info_xlsx:
#     - Updates student information from an XLSX grade file.
#
# 15. is_file_TT:
#     - Checks if the file is an extra-time file and updates the dataframe.
#
# 16. update_TT:
#     - Updates the extra-time column in the dataframe.
#
# 17. find_format_to_update_students_info:
#     - Determines the format of the file and updates student information accordingly.
#
# 18. add_student_grade:
#     - Updates the students' information dataframe with grades and status.
# --------------------------------------------------------------------------------

# --------------------------------------------------------------------------------
# Dependencies:
# --------------------------------------------------------------------------------
# - pandas
# - json
# - os
# - numpy
# --------------------------------------------------------------------------------

import pandas as pd
import json
import os
import numpy as np

def load_teachers(file_path):
    """
    This functiont transform the Json file that contains the teachers from the website into 2 lists
    Args:
        file_path: the path of the Json file that contains the teachers
    Returns:
        list of teachers
        list of the availibility of the teachers
    """    
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
        'Monday Morning': ('Mon_1','Mon_2', 'Mon_3'),
        'Monday Afternoon': ('Mon_4','Mon_5', 'Mon_6'),
        'Tuesday Morning': ('Thu_1','Thu_2', 'Thu_3'),
        'Tuesday Afternoon': ('Thu_4','Thu_5', 'Thu_6'),
        'Wednesday Morning': ('Wed_1','Wed_2', 'Wed_3'),
        'Wednesday Afternoon': ('Wed_4','Wed_5', 'Wed_6'),
        'Thursday Morning': ('Thu_1','Thu_2', 'Thu_3'),
        'Thursday Afternoon': ('Thu_4','Thu_5', 'Thu_6'),
        'Friday Morning': ('Fri_1','Fri_2', 'Fri_3'),
        'Friday Afternoon': ('Fri_4','Fri_5', 'Fri_6'),
        'Saturday Morning': ('Sat_1','Sat_2', 'Sat_3'),
    }

    for teacher in data:
        name_parts = teacher['name'].upper().split()
        FIRSTNAME_parts = teacher['surname'].upper().split()
        email = teacher['email']
        subject = subject_mapping.get(teacher['subject'], teacher['subject'])

        teacher_tuple = (name_parts[0], FIRSTNAME_parts[0], email, subject)
        list_teacher.append(teacher_tuple)

        # Generate the teacher's availability code
        teacher_code = f"{FIRSTNAME_parts[0][:3]}_{subject[:3].upper()}"

        for availability in teacher['availabilities']:
            #print(availability)
            availability_code = day_slot_mapping.get(availability, availability)
            #print(availability_code)
            for i in availability_code:
                list_availability_teachers.append((teacher_code, i))

    return list_teacher, list_availability_teachers


def load_class(file_path):
    """
    This functiont transform the Json file that contains the teachers from the website into 2 lists
    Args:
        file_path: the path of the Json file that contains the teachers
    Returns:
        list of teachers
        list of the availibility of the teachers
    """    
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    list_class = []
    list_availability_class = []

    # Mapping for subject names and abbreviations for availability codes


    day_slot_mapping = {
        'Monday Morning': ('Mon_1','Mon_2', 'Mon_3'),
        'Monday Afternoon': ('Mon_4','Mon_5', 'Mon_6'),
        'Tuesday Morning': ('Thu_1','Thu_2', 'Thu_3'),
        'Tuesday Afternoon': ('Thu_4','Thu_5', 'Thu_6'),
        'Wednesday Morning': ('Wed_1','Wed_2', 'Wed_3'),
        'Wednesday Afternoon': ('Wed_4','Wed_5', 'Wed_6'),
        'Thursday Morning': ('Thu_1','Thu_2', 'Thu_3'),
        'Thursday Afternoon': ('Thu_4','Thu_5', 'Thu_6'),
        'Friday Morning': ('Fri_1','Fri_2', 'Fri_3'),
        'Friday Afternoon': ('Fri_4','Fri_5', 'Fri_6'),
        'Saturday Morning': ('Sat_1','Sat_2', 'Sat_3'),
    }




    return list_class, list_availability_class



def file_data_Student(depot_info_folder): 
    """
    This function uses the files "Student_Info.xlsx" and "Student_Sondage_LV2" to create a dataframe
    that contains all the information of the students, including their second language studied.
    It's also choose the right function to use depending on the format of the files.
    Args:
        depot_info_folder: folder path of the student information
    Return:
        A dataframe containing all the information of the student
    """    
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
    map_school_year(df)
    return df

def map_school_year(df):
    """
    This function remaps the school_year values extracted in the dataframe.
    Args:
        df: The dataframe filled with all the information of the students.
    Returns:
        df: The dataframe with the values in the SCHOOL_YEAR column updated.

    """    
    column = 'SCHOOL_YEAR'
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
    df[column] = df[column].replace(correspondance)
    return df
    
    
def clean_text(text):
    """
    Replace specific unwanted characters in the given text.
    Args:
        text (str): The text to be cleaned.
    Returns:
        str: The cleaned text.
    Example:
        >>> clean_text("R�my")
        'Rémy'
    """
    replacements = {
        '�': 'é',  
    }
    if isinstance(text, str):
        for bad_char, good_char in replacements.items():
            text = text.replace(bad_char, good_char)
    return text

def csv_into_dataframe(file_path, db_column_mapping):
    """
    This function extracts data from the Student_info file in CSV format into a DataFrame
    and maps the columns according to the provided mapping.
    Args:
        file_path: The path of the Student_info.csv file.
        db_column_mapping: The names of the columns matching the database.
    Returns:
        dataframe: A DataFrame containing the data from the CSV.
    """    
    df = pd.read_csv(file_path, encoding='utf-8-sig')
    df = df.applymap(clean_text)    # type: ignore
    df.rename(columns=db_column_mapping, inplace=True)
    df = df[list(db_column_mapping.values())]
    return df

def json_into_dataframe(file_path, db_column_mapping):
    """
    This function extracts data from the Student_info file in JSon format into a DataFrame
    and maps the columns according to the provided mapping.
    Args:
        file_path: The path of the Student_info.json file.
        db_column_mapping: The names of the columns matching the database.
    Returns:
        dataframe: A DataFrame containing the data from the JSon.
    """    
    with open(file_path, 'r', encoding='utf-8-sig') as json_file:
        data = json.load(json_file)
        transformed_data = []
        for item in data:
            transformed_item = {db_column: item.get(json_field) for json_field, db_column in db_column_mapping.items()}
            transformed_data.append(transformed_item)
        df = pd.DataFrame(transformed_data)
    return df

def xlsx_into_dataframe(file_path, db_column_mapping):
    """
    This function extracts data from the Student_info file in xlsx format into a DataFrame
    and maps the columns according to the provided mapping.
    Args:
        file_path: The path of the Student_info.xlsx file.
        db_column_mapping: The names of the columns matching the database.
    Returns:
        dataframe: A DataFrame containing the data from the JSon.
    """
    df = pd.read_excel(file_path)
    df.rename(columns=db_column_mapping, inplace=True)
    df = df[list(db_column_mapping.values())]
    return df


def update_lv2_from_csv(df, file_path):
    """
    This function read the sondage file to update the second language of the students,
    parse it and update the data of the student in the dataframe
    Args:
        df that contains all the students data
        file_path: path of the sondage file
    """    
    csv_reader = pd.read_csv(file_path, encoding='utf-8-sig')
    df = df.applymap(clean_text)
    for index, row in csv_reader.iterrows():
        if ((df['NAME'] == row['Nom']) & (df['FIRSTNAME'] == row['Prénom'])).any():
                df.loc[(df['NAME'] == row['Nom']) & (df['FIRSTNAME'] == row['Prénom']), 'LV2'] = row['Langues']
                
def update_lv2_from_json(df, file_path):
    """
    This function read the sondage file to update the second language of the students,
    parse it and update the data of the student in the dataframe
    Args:
        df that contains all the students data
        file_path: path of the sondage file
    """    
    with open(file_path, 'r', encoding='utf-8-sig') as json_file:
        data = json.load(json_file)
        for row in data:
            if ((df['NAME'] == row['Nom']) & (df['FIRSTNAME'] == row['Prénom'])).any():
                df.loc[(df['NAME'] == row['Nom']) & (df['FIRSTNAME'] == row['Prénom']), 'LV2'] = row['Langues']

def update_lv2_from_xlsx(df, file_path):
    """
    This function read the sondage file to update the second language of the students,
    parse it and update the data of the student in the dataframe
    Args:
        df that contains all the students data
        file_path: path of the sondage file
    """    
    xls_df = pd.read_excel(file_path)
    for index, row in xls_df.iterrows():
        if ((df['NAME'] == row['Nom']) & (df['FIRSTNAME'] == row['Prénom'])).any():
                df.loc[(df['NAME'] == row['Nom']) & (df['FIRSTNAME'] == row['Prénom']), 'LV2'] = row['Langues']
                
def update_student_grade(grade_list, students_info, LV):
    """
    This function parse the grade_list to update the grade of the student in the dataframe.
    It required the name and firstname of the student.
    Args:
        grade_list (df): df of the student grades from 1 file
        students_info (df): df of all the student data
        LV (str): the language of the file
    Returns:
        students_info (df): updated with the grade
    """    
    for index, row in grade_list.iterrows():
        if ((students_info['NAME'] == row['Nom']) & (students_info['FIRSTNAME'] == row['Prénom'])).any():
            students_info.loc[(students_info['NAME'] == row['Nom']) & (students_info['FIRSTNAME'] == row['Prénom']), LV] = row['Note/10,00']
        else:
            print(f"{row['Nom']} {row['Prénom']} doesn't exist")     
    return students_info

def update_students_info_csv(file_path, students_info, LV):
    """
    This function extract the data from a grade file before calling other functions that will update the students_info dataframe.
        file_path (str): path of the grade_list file
        students_info (df): df of all the student data
        LV (str): the language of the file
    Returns:
        students_info (df): updated with the grade
    """    
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
    """
    This function extract the data from a grade file before calling other functions that will update the students_info dataframe.
        file_path (str): path of the grade_list file
        students_info (df): df of all the student data
        LV (str): the language of the file
    Returns:
        students_info (df): updated with the grade
    """    
    with open(file_path, 'r', encoding='utf-8-sig') as jsonfile:
        data = json.load(jsonfile)
        df = pd.DataFrame(data)
        df['Note/10,00'] = df['Note/10,00'].replace('', np.nan).astype(float)
    students_info = update_student_grade(df, students_info, LV)
    students_info = is_file_TT(file_path, students_info, df)
    return students_info

def update_students_info_xlsx(file_path, students_info, LV):
    """
    This function extract the data from a grade file before calling other functions that will update the students_info dataframe.
        file_path (str): path of the grade_list file
        students_info (df): df of all the student data
        LV (str): the language of the file
    Returns:
        students_info (df): updated with the grade
    """
    df = pd.read_excel(file_path)
    df['Note/10,00'] = df['Note/10,00'].replace('', np.nan).astype(float)
    students_info = update_student_grade(df, students_info, LV)
    is_file_TT(file_path, students_info, df)
    return students_info

def is_file_TT(file_path, students_info, grade_list):
    """
    This function check if it's an extra-time file and update the students_info data frame if it's the case.
    Args:
        file_path (str): this contains the name of the file
        students_info (df): df of all the student data
        grade_list (df): df of the student grades from 1 file
    Returns:
        students_info: updated with the TT (tiers-temps/extra-time)
    """    
    if '_TT' in file_path:
        students_info = update_TT(grade_list, students_info)
    return students_info

def update_TT(grade_list, students_info):
    """
    Parse the grade_list to update the extra-time column of the students_info file.
    Args:
        students_info (df): df of all the student data
        grade_list (df): df of the student grades from 1 file
    Returns:
        students_info: updated with the TT (tiers-temps/extra-time)
    """    
    students_info['key'] = students_info['NAME'] + '_' + students_info['FIRSTNAME']
    grade_list['key'] = grade_list['Nom'] + '_' + grade_list['Prénom']

    existing_true_indices = students_info.loc[students_info['REDUCED_EXAM'], 'key'].index
    students_info['REDUCED_EXAM'] = students_info['key'].isin(grade_list['key']) | students_info['REDUCED_EXAM']
    students_info.loc[existing_true_indices, 'REDUCED_EXAM'] = True

    students_info.drop(['key'], axis=1, inplace=True)
    grade_list.drop(['key'], axis=1, inplace=True)
    return students_info

    
def find_format_to_update_students_info(file, depot_note_folder, students_info):
    """
    This function checks the format and name of the file to call the appropriate function with the correct parameters 
    to update the students_info dataframe.
    Args:
        file (srt): name of the grade file
        depot_note_folder (str): name of the grade folder
        students_info (df): df of all the student data  
    """    
    file_path = os.path.join(depot_note_folder, file)
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
    """
    Updates the students' information dataframe with grades and status from the given folder of grade deposits.
    Args:
        depot_note_folder (str): name of the grade folder
        students_info (df): df of all the student data 
    Returns:
        students_info (df): final df of the students data
    """    
    students_info['REDUCED_EXAM'] = False
    for file in [f for f in os.listdir(depot_note_folder)]:
        find_format_to_update_students_info(file, depot_note_folder, students_info)
    #remplit la colonne statut (présent pour tout le monde) et la colonne LV1
    students_info.insert(loc=5, column='STATUS', value='PRESENT')
    students_info.insert(loc=7, column='LV1', value='ANGLAIS')
    students_info['GRADE_LV2'] = students_info['GRADE_LV2'].fillna(0)
    return students_info