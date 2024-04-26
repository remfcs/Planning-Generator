import function_database
import sqlite3
import numpy as np

def number_class(number_student, number_by_class):
    number_class = 0
    # à expliquer 
    if (number_student % number_by_class) > ((number_student //number_by_class)*(2/3)) :
        number_class = number_student//number_by_class + 1
    else :
        number_class = number_student//number_by_class
    
    if  number_class == 0:
        number_class = 1
    return number_class

def make_groups(list_student, number_class):
    print(list_student)
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
    for name_class in function_database.find_list_CLASS(Data):
        nb_forecast = nb_forecast_by_class[name_class]
        if nb_forecast == 0:
            for name_lv2 in function_database.find_list_LV2(Data, name_class):
                if "-débutant (jamais étudié)" in name_lv2 :
                    group = function_database.get_all_students_from_a_year_and_lv2(Data, name_class, name_lv2)
                    group = [pos[0] for pos in group]
                    nb_class = number_class(len(group), nb_by_class)
                    groups = make_groups(group, nb_class)
                    i = 1
                    for group in groups:
                        group_name = 'G' +str(i)        #donner un nom plus explicite 
                        function_database.assigns_groups_to_students(Data, name_class, name_lv2, group_name, group)
                        i+=1
                #c'est la même non?
                # else : 
                #     group = function_database.get_all_students_from_a_year_and_lv2(Data, name_class, name_lv2)
                #     nb_class = number_class(len(group),nb_by_class)
                #     groups = make_groups(group, nb_class)
                #     i = 1
                #     for group in groups:
                #         group_name = 'G' +str(i)        #donner un nom plus explicite
                #         conn = sqlite3.connect(Data)
                #         cursor = conn.cursor()
                #         cursor.execute("INSERT INTO Groups(CLASS, LV, GROUP_LV) VALUES(?,?,?);", (name_class, name_lv2, group_name))
                #         for student in group:
                #             cursor.execute("UPDATE Student SET GROUP_LV2=? WHERE EMAIL=?;", (group_name, student[0]))
                #             conn.commit()  
                #             cursor.fetchall()  
                #         i+=1                                                         
        else :
            conn = sqlite3.connect(Data)
            for name_lv2 in function_database.find_list_LV2(Data, name_class):
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
                    nb_class = number_class(len(group),nb_by_class)
                    groups = make_groups(group, nb_class)
                    i = 1
                    for group in groups:
                        group_name = 'G' +str(i)        #donner un nom plus explicite
                        conn = sqlite3.connect(Data)
                        cursor = conn.cursor()
                        cursor.execute("INSERT INTO Groups(CLASS, LV, GROUP_LV) VALUES(?,?,?);", (name_class, name_lv2, group_name))
                        for student in group:
                            if student !='forecast':
                                cursor.execute("UPDATE Student SET GROUP_LV2=? WHERE EMAIL=?;", (group_name, student))
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
                    nb_class = number_class(len(group),nb_by_class)
                    groups = make_groups(group, nb_class)
                    i = 1
                    for group in groups:
                        group_name = 'G' +str(i)        #donner un nom plus explicite
                        cursor = conn.cursor()
                        cursor.execute("INSERT INTO Groups(CLASS, LV, GROUP_LV) VALUES(?,?,?);", (name_class, name_lv2, group_name))
                        for student in group:
                            if student !='forecast':
                                cursor.execute("UPDATE Student SET GROUP_LV2=? WHERE EMAIL=?;", (group_name, student[0]))
                                conn.commit()  
                                cursor.fetchall()  
                        i+=1
            conn.close()
    return 
