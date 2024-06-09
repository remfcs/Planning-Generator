def make_association(Data, promo_pair):
    conn = sqlite3.connect(Data)  # Connect to the SQLite database
    for promo_list in promo_pair:
        list_slots = function_database.get_lv_slot(Data, promo_list)  # Get the list of slots for the promo list
        list_lv2 = function_database.find_list_LV2(Data, promo_list)  # Get list of LV2 languages for the promo list
        list_lv1 = function_database.find_list_LV1(Data, promo_list)  # Get list of LV1 languages for the promo list
        list_lv = list_lv1 + list_lv2  # Combine both lists of languages
        list_lv_check = []  # Initialize a list to keep track of checked languages
        insertions = []  # Initialize a list to store insertions
        final_insertions = []  # Initialize a list to store final insertions

        for lv in list_lv:
            lv_bis = lv
            if '-débutant' in lv_bis:
                lv_bis = lv_bis.split(' -débutant')[0]  # Remove '-débutant' suffix for comparison

            if lv_bis not in list_lv_check:
                teacher_availabilities = function_database.get_available_teacher2(Data, list_slots, lv_bis)  # Get available teachers for the language
                list_lv_check.append(lv_bis)  # Mark the language as checked

                cursor = conn.cursor()
                pattern = '%' + lv_bis[:3] + '%'  # Create a pattern to match courses for the language
                cursor.execute("SELECT DISTINCT(ID_COURSE) FROM List_Groups_Students WHERE ID_COURSE LIKE ? ORDER BY LENGTH(ID_COURSE), ID_COURSE;", (pattern,))
                list_groups = cursor.fetchall()
                list_groups = [pos[0] for pos in list_groups]  # Extract course IDs

                if len(teacher_availabilities) > len(list_groups):
                    print("teacher_availabilities > list_groups")
                elif len(teacher_availabilities) < len(list_groups):
                    print("teacher_availabilities < list_groups")
                else:
                    for i in range(len(teacher_availabilities)):
                        insertion = (teacher_availabilities[i][0], list_groups[i], teacher_availabilities[i][1], teacher_availabilities[i][0][4:])
                        insertions.append(insertion)  # Prepare insertions of teacher and group associations

        for slot in list_slots:
            rooms_available = function_database.get_available_room(Data, slot)  # Get available rooms for the slot

            for i in range(len(insertions)):
                if insertions[i][2] == slot[0]:  # Match insertions with the current slot
                    if rooms_available:
                        room = rooms_available.pop(0)  # Get the first available room and remove it from the list
                    else:
                        room = ('No more available',)
                    final_insertion = insertions[i] + room  # Add room information to the insertion
                    final_insertions.append(final_insertion)  # Add to the final insertions list

        for value in final_insertions:
            result_str = ', '.join(promo_list)  # Create a string representation of the promo list
            cursor.execute("INSERT INTO Courses(LANGUAGE, ID_COURSE, ID_TEACHER, ID_AVAILABILITY, ID_ROOM, PROMO) VALUES(?, ?, ?, ?, ?, ?);", 
                           (value[3], value[1], value[0], value[2], value[4], result_str))
            conn.commit()  # Insert the final insertion into the Courses table and commit the changes

    conn.close()  # Close the database connection