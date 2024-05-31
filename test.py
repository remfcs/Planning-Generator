import sqlite3
import function_create_groups
import function_read_folder 
import function_database
import function_file_db
import function_conflict


Data = 'data/test.sqlite3'
max_by_class = 16

from concurrent.futures import ThreadPoolExecutor

n = 0
max_iterations = 2

with ThreadPoolExecutor() as executor:
    while n < max_iterations:
        for i in range(15):
            future_conflict_resolution = executor.submit(function_conflict.resolution_conflict, Data)
            future_conflict_resolution.result()  # Attendre la fin de la tâche

            function_conflict.balance_groups(Data, max_by_class)

        function_conflict.resolution_conflict_inverse(Data)
        function_conflict.balance_groups(Data, max_by_class)

        n += 1

print(function_conflict.get_nb_student_by_group(Data))
print(len(function_conflict.get_students_with_schedule_conflicts(Data)))
print(function_conflict.get_students_with_schedule_conflicts(Data))




