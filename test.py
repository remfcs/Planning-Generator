def make_groups(Data, promo_pair, max_by_class):
    conn = sqlite3.connect(Data)
    list_lv = function_database.find_list_lv(Data)
    while list_lv:
        #print(list_lv)
        lv = list_lv.pop(0)
        deb = 0
        if '-débutant' in lv:
            lv = lv.split(' -débutant')[0]
            deb = 1
        promo_list = promo_pair[lv]
        if lv + " -débutant (jamais étudié)" in list_lv:
            list_lv.remove(lv + " -débutant (jamais étudié)")
            deb = 2
        promo_list = promo_pair[lv]
        
        slots = {}
        for promo_association in promo_list :
            list_slots = function_database.get_lv_slot(Data, promo_association)
            name = ', '.join(f"'{item}'" for item in promo_association)
            slots[name] = list_slots

        for promo_association in promo_list :
            name = ', '.join(f"'{item}'" for item in promo_association)
            element_to_keys = {}

            # Parcourir les éléments de slots
            for key, value in slots.items():
                for element in value:
                    if element not in element_to_keys:
                        element_to_keys[element] = []
                    element_to_keys[element].append(key)
            #print(element_to_keys)
            # Afficher les clés des éléments partagés

            def get_students_and_nb_students(lv, promo_association):
                students = { }
                if deb ==0 :
                    students[lv ] = []
                elif deb == 1 :
                    students[lv + " -débutant (jamais étudié)"] = []
                elif deb == 2 :
                    students[lv ] = []
                    students[lv + " -débutant (jamais étudié)"] = []
                for promo in promo_association:
                    for i in students :
                        if "-débutant (jamais étudié)" in i:
                            cursor = conn.cursor()
                            # Get the list of beginner students for the specific language and promo
                            cursor.execute("SELECT EMAIL FROM Student WHERE (LV1 = ? OR LV2 = ?) AND SCHOOL_YEAR = ?;",(i, i, promo))
                            student = cursor.fetchall()
                            student = [pos[0] for pos in student]  # Extract student emails
                        else:
                            cursor = conn.cursor()
                            query = """
                            SELECT EMAIL, 
                                CASE 
                                    WHEN LV1 = ? THEN GRADE_LV1 
                                    WHEN LV2 = ? THEN GRADE_LV2 
                                END AS GRADE 
                            FROM Student 
                            WHERE (LV1 = ? OR LV2 = ?) AND SCHOOL_YEAR = ?
                            ORDER BY GRADE DESC;
                            """
                            # Get the list of non-beginner students sorted by their grades for the specific language and promo
                            cursor.execute(query, (i, i, i, i, promo))
                            student = cursor.fetchall()
                            student = [pos[0] for pos in student]  # Extract student emails

                        students[i] += student  # Add the students to the list
                nb_students =0 
                for key, value in students.items():
                    nb_students += len(value)
                    #print(lv, promo_association,f"Clé : {key}, Nombre d'éléments : {len(value)}")
                #print(promo_association, next(iter(students.keys())))
                return students, nb_students
            print(lv, promo_association)
            sum = 0
            liste = []
            for element, keys in element_to_keys.items():
                print(element, keys)
                if len(keys) > 1:
                    for i in keys :
                        i2 = [item.strip("'") for item in i.split(', ')]
                        print("debut",i2)
                        if  (i2 != promo_association) & (i2 not in liste):
                            liste.append(i2)
                            R, num = get_students_and_nb_students(lv, i2)
                            sum += num
                            print(liste, sum)

            students, nb_students = get_students_and_nb_students(lv, promo_association)
            print(sum, nb_students)
            nb_class = nomber_class(sum,nb_students, Data, students, promo_association,  max_by_class)  # Calculate the number of classes needed
            print(nb_class)

            for key, value in nb_class.items():
                students2 = students[key]
                groups = make_group(students2, value)  # Create groups based on the number of classes
                language = "_" + key[:3]  # Extract language abbreviation
                name = ""
                if "-débutant (jamais étudié)" in lv:
                    name = "_D"  # Append '_D' for beginner groups
                i = 1
                result_str = ', '.join(promo_association)  # Create a string representation of the promo list
                #print(groups)
                for group in groups:  # type: ignore
                    group_name = 'G' + str(i) + "_{" + result_str + "}" + language + name  # Create a unique group name
                    for student in group:
                        cursor = conn.cursor()
                        cursor.execute("INSERT INTO List_Groups_Students(ID_COURSE, ID_STUDENT) VALUES(?, ?);", (group_name, student))
                        conn.commit()  # Insert each student into the group and commit the changes
                    i += 1  # Increment the group counter

    conn.close()  # Close the database connection
    return
   