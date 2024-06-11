import pdfkit # type: ignore
import logging
from flask import Flask, jsonify, request, send_from_directory, send_file, make_response
import os
import webbrowser
import threading
import json
import subprocess
import sqlite3
import csv
import io
import pandas as pd

app = Flask(__name__, static_url_path='', static_folder='.')

# Configurez le logging
logging.basicConfig(level=logging.DEBUG)

# Détermine le chemin absolu du répertoire du projet
project_dir = os.path.dirname(os.path.abspath(__file__))
# Chemin relatif vers wkhtmltopdf
path_wkhtmltopdf = os.path.join(project_dir, 'Export', 'wkhtmltopdf', 'bin', 'wkhtmltopdf.exe')

logging.debug(f"Using wkhtmltopdf path: {path_wkhtmltopdf}")
config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)

UPLOAD_FOLDER = './data/uploads'
UPLOAD_FOLDER_LEVEL = './data/uploads/input_level'
UPLOAD_FOLDER_INFO = './data/uploads/input_info'
TEACHERS_JSON_PATH = os.path.join(UPLOAD_FOLDER, 'teachers.json')
PROMO_AVAILABILITIES_PATH= os.path.join(UPLOAD_FOLDER, 'promo_availabilities.json')
DATABASE_PATH = './data/database.sqlite3'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOAD_FOLDER_INFO'] = UPLOAD_FOLDER_INFO
app.config['UPLOAD_FOLDER_LEVEL'] = UPLOAD_FOLDER_LEVEL

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(UPLOAD_FOLDER_LEVEL, exist_ok=True)
os.makedirs(UPLOAD_FOLDER_INFO, exist_ok=True)

@app.route('/start')
def start():
    return send_from_directory('.', 'start/start.html')

@app.route('/create_planning', methods=['POST'])
def submit():
    # Récupérer les valeurs des champs de formulaire
    estimate_number_student = request.form.get('estimate_number_student')
    halfday_slot = request.form.get('halfday_slot')
    
    availability_Promo_json= request.form.get('availabilityPromo', '[]')
    availability_Promo = json.loads(availability_Promo_json)
    with open(PROMO_AVAILABILITIES_PATH, 'w') as json_file:
        json.dump(availability_Promo, json_file, indent=4)

    # Récupérer les fichiers uploadés
    students_files = request.files.getlist('students_files[]')
    level_files = request.files.getlist('level_files[]')

    # Enregistrer les fichiers uploadés
    saved_files = {'students_files': [], 'level_files': []}

    for file in students_files:
        if file.filename:
            file_path = os.path.join(app.config['UPLOAD_FOLDER_INFO'], file.filename)
            file.save(file_path)
            saved_files['students_files'].append(file.filename)

    for file in level_files:
        if file.filename:
            file_path = os.path.join(app.config['UPLOAD_FOLDER_LEVEL'], file.filename)
            file.save(file_path)
            saved_files['level_files'].append(file.filename)

    teachers_json = request.form.get('teachers', '[]')  # Default to an empty list as JSON
    teachers = json.loads(teachers_json)  # Decode the JSON string
    with open(TEACHERS_JSON_PATH, 'w') as json_file:
        json.dump(teachers, json_file, indent=4)

    response_data = {
        "estimation": f"Estimation du nombre de nouveaux étudiants: {estimate_number_student}",
        "halfday_slots": f"Nombre de demi-journées: {halfday_slot}",
        "students_files": ", ".join(saved_files['students_files']),
        "level_files": ", ".join(saved_files['level_files']),
        "teacher:": teachers, 
        "Promo availabilities": availability_Promo
    }
    try:
        # Exécuter le script main.py
        result = subprocess.run(['python', './main.py'], capture_output=True, text=True)

        if result.returncode == 0:
            return jsonify({"status": "success", "message": result.stdout.strip()})
        else:
            return jsonify({"status": "error", "message": result.stderr.strip()})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/create_planning', methods=['POST'])
def create_planning_route():
    try:
        # Exécuter le script main.py
        result = subprocess.run(['python', './main.py'], capture_output=True, text=True)

        if result.returncode == 0:
            return jsonify({"status": "success", "message": result.stdout.strip()})
        else:
            return jsonify({"status": "error", "message": result.stderr.strip()})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

def get_student_details(name=None, niveau=None, professeur=None, langue=None, group_lv1=None):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    query = """
    SELECT s.NAME, s.SURNAME, s.EMAIL, s.SCHOOL_YEAR, c.ID_GROUP, c.Language, t.NAME AS TeacherName, t.SURNAME AS TeacherSurname
    FROM Student s
    LEFT JOIN List_Groups_Students lg ON s.EMAIL = lg.ID_STUDENT
    LEFT JOIN Courses c ON lg.ID_COURSE = c.ID_COURSE
    LEFT JOIN Teachers t ON c.ID_Teacher = t.ID_Teacher
    WHERE 1=1
    """
    params = []

    if name:
        query += " AND LOWER(s.NAME) LIKE ?"
        params.append(f"%{name}%")
    if niveau:
        query += " AND s.SCHOOL_YEAR LIKE ?"
        params.append(f"{niveau}%")
    if professeur:
        query += " AND (t.NAME || ' ' || t.SURNAME) = ?"
        params.append(professeur)
    if langue:
        query += " AND c.Language = ?"
        params.append(langue)
    if group_lv1:
        query += " AND c.ID_GROUP = ?"
        params.append(group_lv1)

    cursor.execute(query, params)
    rows = cursor.fetchall()

    students = []
    for row in rows:
        student = {
            "Surname": row[0],
            "Name": row[1],
            "Email": row[2],
            "Class": row[3],
            "GROUP_LV1": row[4],
            "Language": row[5],
            "TeacherName": row[6],
            "TeacherSurname": row[7]
        }
        students.append(student)

    conn.close()
    return students

@app.route('/')
def index():
    return send_from_directory('.', 'Home Page/home.html')

@app.route('/students')
def get_students():
    name = request.args.get('name')
    niveau = request.args.get('niveau')
    professeur = request.args.get('professeur')
    langue = request.args.get('langue')
    group_lv1 = request.args.get('group_lv1')
    students = get_student_details(name, niveau, professeur, langue, group_lv1)
    return jsonify(students)

def get_professors():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    # Récupérer les informations des professeurs avec la disponibilité combinée et les groupes distincts
    cursor.execute("""
        SELECT T.name, T.surname, T.mail, T.Subject, 
               GROUP_CONCAT(DISTINCT A.Day || ' ' || A.Hour) as availabilities,
               GROUP_CONCAT(DISTINCT C.ID_GROUP || ' (' || A.Day || ' ' || A.Hour || ')') as groups
        FROM Teachers T
        LEFT JOIN Availability_Teachers AT ON T.ID_Teacher = AT.ID_Teacher
        LEFT JOIN Availabilities A ON AT.ID_Availability = A.ID_Availability
        LEFT JOIN Courses C ON T.ID_Teacher = C.ID_Teacher
        GROUP BY T.name, T.surname, T.mail, T.Subject
    """)
    professors = cursor.fetchall()
    conn.close()
    return professors

@app.route('/api/professors', methods=['GET'])
def api_professors():
    language = request.args.get('language')
    group = request.args.get('group')

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    query = """
        SELECT T.name, T.surname, T.mail, T.Subject, 
               GROUP_CONCAT(A.Day || ' ' || A.Hour) as availabilities
        FROM Teachers T
        LEFT JOIN Availability_Teachers AT ON T.ID_Teacher = AT.ID_Teacher
        LEFT JOIN Availabilities A ON AT.ID_Availability = A.ID_Availability
        WHERE 1=1
    """
    params = []

    if language:
        query += " AND T.Subject LIKE ?"
        params.append(f"%{language}%")
    if group:
        query += " AND T.ID_Teacher IN (SELECT ID_Teacher FROM Courses WHERE ID_COURSE = ?)"
        params.append(group)

    query += " GROUP BY T.name, T.surname, T.mail, T.Subject"

    cursor.execute(query, params)
    professors = cursor.fetchall()
    conn.close()

    professor_list = []
    for professor in professors:
                professor_list.append({
            "name": professor[0],
            "surname": professor[1],
            "email": professor[2],
            "subject": professor[3],
            "availability": professor[4]
        })
    return jsonify(professor_list)

def get_professor_details(professor_name):
    if not professor_name:
        return {}

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    name_parts = professor_name.split()
    if len(name_parts) < 2:
        return {}  # Nom de professeur invalide

    first_name = name_parts[0]
    last_name = name_parts[1]

    cursor.execute("""
        SELECT t.name, t.surname, t.mail, t.Subject, 
               GROUP_CONCAT(A.Day || ' ' || A.Hour) as availabilities
        FROM Teachers t
        LEFT JOIN Availability_Teachers AT ON t.ID_Teacher = AT.ID_Teacher
        LEFT JOIN Availabilities A ON AT.ID_Availability = A.ID_Availability
        WHERE t.name = ? AND t.surname = ?
        GROUP BY t.name, t.surname, t.mail, t.Subject
    """, (first_name, last_name))

    row = cursor.fetchone()
    if not row:
        return {}

    professor = {
        'name': row[0],
        'surname': row[1],
        'email': row[2],
        'subject': row[3],
        'availability': row[4]
    }

    cursor.execute("""
        SELECT DISTINCT Language
        FROM Courses
        WHERE ID_Teacher IN (
            SELECT ID_Teacher 
            FROM Teachers 
            WHERE name = ? AND surname = ?
        )
    """, (first_name, last_name))
    languages = [row[0] for row in cursor.fetchall()]

    cursor.execute("""
        SELECT DISTINCT ID_GROUP
        FROM Courses
        WHERE ID_Teacher IN (
            SELECT ID_Teacher 
            FROM Teachers 
            WHERE name = ? AND surname = ?
        )
    """, (first_name, last_name))
    groups = [row[0] for row in cursor.fetchall()]

    professor['languages'] = languages
    professor['groups'] = groups

    conn.close()

    return professor

@app.route('/api/professor_details', methods=['GET'])
def professor_details():
    professor_name = request.args.get('professor')
    details = get_professor_details(professor_name)
    return jsonify(details)

@app.route('/languages')
def get_languages():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    query = "SELECT DISTINCT Language FROM Courses"
    cursor.execute(query)
    languages = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    return jsonify(languages)

@app.route('/groups')
def get_groups():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    query = "SELECT DISTINCT ID_GROUP FROM Courses"
    cursor.execute(query)
    groups = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    return jsonify(groups)

@app.route('/groups/<promo>/<language>')
def get_courses_by_promo(promo, language):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    query = """
    SELECT c.ID_GROUP, c.ID_AVAILABILITY, c.PROMO, c.ID_COURSE, COUNT(lgs.ID_STUDENT) AS student_count
    FROM Courses c
    LEFT JOIN List_Groups_Students lgs ON c.ID_COURSE = lgs.ID_COURSE
    WHERE c.LANGUAGE LIKE ? AND c.PROMO LIKE ?
    GROUP BY c.ID_GROUP, c.ID_AVAILABILITY, c.PROMO, c.ID_COURSE
    """
    cursor.execute(query, ('%' + language + '%', '%' + promo + '%'))
    groups = cursor.fetchall()
    conn.close()
    result = []
    for group in groups:
        result.append({
            'ID_GROUP': group[0],
            'ID_AVAILABILITY': group[1],
            'PROMO': group[2],
            'ID_COURSE': group[3],
            'student_count': group[4]
        })
    return jsonify(result)

@app.route('/add', methods=['POST'])
def add_student():
    data = request.get_json()
    new_student = (
        data['email'],
        data['name'],
        data['surname'],
        data['school_year'],
        data['lv1'],
        data['lv2'],
        1 if data['reducedExam'] else 0
    )
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT CASE WHEN EXISTS (
            SELECT 1
            FROM Student
            WHERE EMAIL = ?
            ) THEN 'true' ELSE 'false' END
            """, (data['email'],))
        exists = cursor.fetchone()[0]
        if exists == 'true':
            return jsonify({'status': 'error', 'message': 'Student already exists'})
        else:
            cursor.execute("""
                INSERT INTO Student (EMAIL, NAME, SURNAME, SCHOOL_YEAR, LV1, LV2, REDUCED_EXAM)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, new_student)
            conn.commit()
            return jsonify({'status': 'success'})
    finally:
        conn.close()

@app.route('/add2', methods=['POST'])
def add_list():
    data_english = request.get_json()
    new_english_course = (
        data_english['english'],
        data_english['email']
    )
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO List_Groups_Students (ID_COURSE, ID_STUDENT)
        VALUES (?, ?)
        """, new_english_course)
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

@app.route('/add3', methods=['POST'])
def add_list2():
    data_lv2 = request.get_json()
    new_lv2_course = (
        data_lv2['lv2'],
        data_lv2['email']
    )
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO List_Groups_Students (ID_COURSE, ID_STUDENT)
        VALUES (?, ?)
        """, new_lv2_course)
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

@app.route('/deleteStudent', methods=['POST'])
def delete_student():
    data = request.get_json()
    email = data['email']
    print(email)
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Student WHERE EMAIL = ?", (email,))
    cursor.execute("DELETE FROM List_Groups_Students WHERE ID_STUDENT = ?", (email,))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

@app.route('/timeslot')
def get_timeslot():
    course = request.args.get('course')
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT ID_AVAILABILITY FROM Courses WHERE ID_COURSE LIKE ?", (course,))
        timeslot = cursor.fetchone()
        if timeslot is None:
            return jsonify({"error": "No timeslot found"}), 404
        return jsonify({"timeslot": timeslot[0]})
    finally:
        cursor.close()
        conn.close()

@app.route('/professors')
def serve_professors_html():
    return send_from_directory('.', 'professors.html')

@app.route('/script.js')
def serve_script_js():
    return send_from_directory('.', 'script.js')

@app.route('/style.css')
def serve_style_css():
    return send_from_directory('.', 'style.css')

@app.route('/home.html')
def serve_home_html():
    return send_from_directory('.', 'home.html')

@app.route('/modifications')
def modifications():
    return send_from_directory('.', 'Modify_student/add-student.html')

@app.route('/export')
def export_page():
    return send_from_directory('Export', 'Export.html')

@app.route('/export.js')
def serve_export_js():
    return send_from_directory('Export', 'export.js')

@app.route('/export_group', methods=['GET'])
def export_group():
    file_type = request.args.get('fileType')
    group_id = request.args.get('groupId')
    export_all = request.args.get('exportAll', 'false') == 'true'

    logging.debug(f"Received parameters for export_group - fileType: {file_type}, groupId: {group_id}, exportAll: {export_all}")

    if not file_type:
        return "Missing fileType parameter", 400

    if file_type == 'pdf':
        if export_all:
            return export_all_groups()
        elif group_id:
            return generate_group_pdf(group_id)
        else:
            return "Missing groupId parameter", 400
    elif file_type == 'csv':
        if export_all:
            return export_all_groups_csv()
        elif group_id:
            return generate_group_csv(group_id)
        else:
            return "Missing groupId parameter", 400

    return "Invalid file type", 400

@app.route('/export_professor', methods=['GET'])
def export_professor():
    file_type = request.args.get('fileType')
    professor_name = request.args.get('professor')
    export_all = request.args.get('exportAll', 'false') == 'true'

    logging.debug(f"Received parameters for export_professor - fileType: {file_type}, professorName: {professor_name}, exportAll: {export_all}")

    if not file_type:
        return "Missing fileType parameter", 400

    if file_type == 'pdf':
        if export_all:
            return generate_professors_pdf()
        elif professor_name:
            return generate_professor_pdf(professor_name)
        else:
            return "Missing professorId parameter", 400
    elif file_type == 'csv':
        if export_all:
            return generate_professors_csv()
        elif professor_name:
            return generate_professor_csv(professor_name)
        else:
            return "Missing professorId parameter", 400

    return "Invalid file type", 400

def export_all_groups():
    groups_response = get_groups()
    if groups_response.status_code != 200:
        return "Failed to get groups", 500

    groups = groups_response.get_json()
    if not groups:
        return "No groups found", 400

    html_content = """
    <html>
    <head>
        <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            line-height: 1.6;
            color: #333;
        }
        h1, h2 {
            color: #2c3e50;
            border-bottom: 2px solid #2c3e50;
            padding-bottom: 10px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
            font-size: 0.9em;
            background-color: #f2f2f2;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 12px 15px;
            text-align: left;
        }
        th {
            background-color: #2980b9;
            color: white;
            text-transform: uppercase;
        }
        tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        tr:hover {
            background-color: #f1f1f1;
        }
        </style>
    </head>
    <body>
    <h1>All Groups</h1>
    """

    for group_id in groups:
        students = get_student_details(group_lv1=group_id)
        teacher_info = get_teacher_by_group(group_id)

        if not teacher_info:
            teacher_name = "Unknown"
        else:
            teacher_name = f"{teacher_info['name']} {teacher_info['surname']}"

        # Fetch the day and time from the Courses and Availabilities tables
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT A.Day, A.Hour
            FROM Courses C
            JOIN Availabilities A ON C.ID_Availability = A.ID_Availability
            WHERE C.ID_GROUP = ?
        """, (group_id,))
        availability = cursor.fetchone()
        conn.close()

        if availability:
            day = availability[0]
            time = availability[1]
        else:
            day = 'Unknown'
            time = 'Unknown'

        html_content += f"""
        <h2>Group {group_id}</h2>
        <h3>Teacher: {teacher_name}</h3>
        <h3>Schedule: {day} {time}</h3>
        <table>
            <thead>
                <tr>
                    <th>Name</th>
                    <th>Surname</th>
                    <th>Email</th>
                    <th>Class</th>
                </tr>
            </thead>
            <tbody>
        """
        for student in students:
            html_content += f"""
                <tr>
                    <td>{student['Name']}</td>
                    <td>{student['Surname']}</td>
                    <td>{student['Email']}</td>
                    <td>{student['Class']}</td>
                </tr>
            """
        html_content += """
            </tbody>
        </table>
        """
    html_content += """
    </body>
    </html>
    """

    output_path = "./all_groups.pdf"
    absolute_output_path = os.path.abspath(output_path)

    pdfkit.from_string(html_content, output_path, configuration=config)

    if not os.path.exists(absolute_output_path):
        return "Failed to create PDF file", 500

    return send_file(absolute_output_path, as_attachment=True, download_name='all_groups.pdf')

def generate_professors_pdf():
    professors = get_professors_with_groups()
    html_content = """
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; color: #333; }
            h1 { color: #2c3e50; border-bottom: 2px solid #2c3e50; padding-bottom: 10px; }
            table { width: 100%; border-collapse: collapse; margin-bottom: 20px; font-size: 0.9em; background-color: #f2f2f2; }
            th, td { border: 1px solid #ddd; padding: 12px 15px; text-align: left; }
            th { background-color: #2980b9; color: white; text-transform: uppercase; }
            tr:nth-child(even) { background-color: #f9f9f9; }
            tr:hover { background-color: #f1f1f1; }
        </style>
    </head>
    <body>
        <h1>Professors List</h1>
        <table>
            <thead>
                <tr>
                    <th>Name</th>
                    <th>Surname</th>
                    <th>Email</th>
                    <th>Subject</th>
                    <th>Availability</th>
                    <th>Groups</th>
                </tr>
            </thead>
            <tbody>
    """

    for professor in professors:
        name, surname, email, subject, availability, groups = professor
        availability = "<br>".join(set(availability.split(','))) if availability else ""

        # Fetch groups and schedules for the professor
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT C.ID_GROUP, A.Day, A.Hour
            FROM Courses C
            JOIN Availabilities A ON C.ID_Availability = A.ID_Availability
            WHERE C.ID_Teacher = (SELECT ID_Teacher FROM Teachers WHERE name = ? AND surname = ?)
        """, (name, surname))
        group_schedules = cursor.fetchall()
        conn.close()

        if group_schedules:
            formatted_groups = []
            for group_id, day, time in group_schedules:
                formatted_group = f"{group_id} ({day} {time})"
                formatted_groups.append(formatted_group)

            # Remove duplicates while preserving order
            unique_groups = list(dict.fromkeys(formatted_groups))
            groups_html = "<br>".join(unique_groups)
        else:
            groups_html = ""

        html_content += f"""
            <tr>
                <td>{name}</td>
                <td>{surname}</td>
                <td>{email}</td>
                <td>{subject}</td>
                <td>{availability}</td>
                <td>{groups_html}</td>
            </tr>
        """

    html_content += """
            </tbody>
        </table>
    </body>
    </html>
    """

    pdf = pdfkit.from_string(html_content, False, configuration=config)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=professors_list.pdf'
    return response

def get_professors_with_groups():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT T.name, T.surname, T.mail, T.Subject, 
               GROUP_CONCAT(DISTINCT A.Day || ' ' || A.Hour) as availabilities,
               GROUP_CONCAT(DISTINCT C.ID_GROUP || ' (' || A.Day || ' ' || A.Hour || ')') as groups
        FROM Teachers T
        LEFT JOIN Availability_Teachers AT ON T.ID_Teacher = AT.ID_Teacher
        LEFT JOIN Availabilities A ON AT.ID_Availability = A.ID_Availability
        LEFT JOIN Courses C ON T.ID_Teacher = C.ID_Teacher
        GROUP BY T.name, T.surname, T.mail, T.Subject
    """)
    professors = cursor.fetchall()
    conn.close()
    return professors

def generate_professors_csv():
    professors = get_professors()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Name", "Surname", "Email", "Subject", "Availability", "Groups"])

    for professor in professors:
        name, surname, email, subject, availability, groups = professor

        # Process availability
        availability = availability.replace(",", ", ") if availability else ""

        # Fetch groups and schedules for the professor
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT C.ID_GROUP, A.Day, A.Hour
            FROM Courses C
            JOIN Availabilities A ON C.ID_Availability = A.ID_Availability
            WHERE C.ID_Teacher = (SELECT ID_Teacher FROM Teachers WHERE name = ? AND surname = ?)
        """, (name, surname))
        group_schedules = cursor.fetchall()
        conn.close()

        if group_schedules:
            formatted_groups = []
            for group_id, day, time in group_schedules:
                formatted_group = f"{group_id} ({day} {time})"
                formatted_groups.append(formatted_group)

            # Remove duplicates while preserving order
            unique_groups = list(dict.fromkeys(formatted_groups))
            groups = ', '.join(unique_groups)
        else:
            groups = ""

        writer.writerow([name, surname, email, subject, availability, groups])

    output.seek(0)
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=professors_list.csv'
    response.headers['Content-Type'] = 'text/csv'
    return response

def generate_group_csv(group_id):
    students = get_student_details(group_lv1=group_id)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Surname", "Name", "Email", "Class", "GROUP_LV1", "Language", "TeacherName", "TeacherSurname"])
    for student in students:
        writer.writerow([student["Surname"], student["Name"], student["Email"], student["Class"], student["GROUP_LV1"], student["Language"], student["TeacherName"], student["TeacherSurname"]])
    output.seek(0)
    response = make_response(output.getvalue())
    logging.debug(f"Setting Content-Disposition header for group {group_id}")
    response.headers['Content-Disposition'] = f'attachment; filename="group_{group_id}.csv"'
    response.headers['Content-Type'] = 'text/csv'
    return response

def export_all_groups_csv():
    response = get_groups()
    if response.status_code != 200:
        logging.error(f"Failed to get groups: {response.status_code}")
        return "Failed to get groups", 500

    groups = response.get_json()
    if not groups:
        logging.error("No groups found")
        return "No groups found", 400

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["GroupID", "Surname", "Name", "Email", "Class", "GROUP_LV1", "Language", "TeacherName", "TeacherSurname", "Day", "Time"])

    for group in groups:
        students = get_student_details(group_lv1=group)
        for student in students:
            teacher_name = student.get('TeacherName', 'Unknown')
            teacher_surname = student.get('TeacherSurname', 'Unknown')

            # Fetch the day and time from the Courses and Availabilities tables
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT A.Day, A.Hour
                FROM Courses C
                JOIN Availabilities A ON C.ID_Availability = A.ID_Availability
                WHERE C.ID_GROUP = ?
            """, (student['GROUP_LV1'],))
            availability = cursor.fetchone()
            conn.close()

            if availability:
                day = availability[0]
                time = availability[1]
            else:
                day = 'Unknown'
                time = 'Unknown'

            writer.writerow([group, student['Surname'], student['Name'], student['Email'], student['Class'], student['GROUP_LV1'], student['Language'], teacher_name, teacher_surname, day, time])

    output.seek(0)
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=all_groups.csv'
    response.headers['Content-Type'] = 'text/csv'
    return response

def generate_professor_csv(professor_name):
    professor_details = get_professor_details(professor_name)
    if not professor_details:
        return "No professor details found", 404

    print(f"Professor details for {professor_name}: {professor_details}")  # Debug print

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Name", "Surname", "Email", "Subject", "Availability", "Groups"])

    # Since professor_details is a dictionary, we directly extract the fields
    name = professor_details.get('name')
    surname = professor_details.get('surname')
    email = professor_details.get('email')
    subject = professor_details.get('subject')
    availability = professor_details.get('availability', '')

    # Process availability
    availability = availability.replace(",", ", ") if availability else ""

    # Fetch and process groups
    groups = get_professor_groups(professor_name)
    print(f"Groups for {professor_name}: {groups}")  # Debug print

    # Create a dictionary to store each group and its unique time slot
    group_dict = {}
    for group in groups:
        group_name = group[0]
        group_time = f"{group[1]} {group[2]}"
        group_dict[group_name] = group_time

    # Convert the dictionary to a list of unique groups with their times
    unique_groups = [f"{group} ({time})" for group, time in group_dict.items()]

    groups_str = ', '.join(unique_groups)

    writer.writerow([name, surname, email, subject, availability, groups_str])

    output.seek(0)
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = f'attachment; filename=professor_{professor_name}.csv'
    response.headers['Content-Type'] = 'text/csv'
    return response

def generate_group_pdf(group_id):
    students = get_student_details(group_lv1=group_id)
    teacher_info = get_teacher_by_group(group_id)  # Assuming you have a function to fetch the teacher by group

    if not teacher_info:
        return "No teacher found for this group", 404

    teacher_name = f"{teacher_info['name']} {teacher_info['surname']}"

    # Fetch the day and time from the Courses and Availabilities tables
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT A.Day, A.Hour
        FROM Courses C
        JOIN Availabilities A ON C.ID_Availability = A.ID_Availability
        WHERE C.ID_GROUP = ?
    """, (group_id,))
    availability = cursor.fetchone()
    conn.close()

    if availability:
        day = availability[0]
        time = availability[1]
    else:
        day = 'Unknown'
        time = 'Unknown'

    html_content = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            line-height: 1.6;
            color: #333;
        }}
        h1, h2 {{
            color: #2c3e50;
            border-bottom: 2px solid #2c3e50;
            padding-bottom: 10px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
            font-size: 0.9em;
            background-color: #f2f2f2;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px 15px;
            text-align: left;
        }}
        th {{
            background-color: #2980b9;
            color: white;
            text-transform: uppercase;
        }}
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        tr:hover {{
            background-color: #f1f1f1;
        }}
        </style>
    </head>
    <body>
        <h1>Group {group_id}</h1>
        <h2>Teacher: {teacher_name}</h2>
        <h2>Schedule: {day} {time}</h2>
        <h2>Students</h2>
        <table>
            <thead>
                <tr>
                    <th>Name</th>
                    <th>Surname</th>
                    <th>Email</th>
                    <th>Class</th>
                </tr>
            </thead>
            <tbody>
    """

    for student in students:
        html_content += f"""
                <tr>
                    <td>{student['Name']}</td>
                    <td>{student['Surname']}</td>
                    <td>{student['Email']}</td>
                    <td>{student['Class']}</td>
                </tr>
        """
    html_content += """
            </tbody>
        </table>
    </body>
    </html>
    """

    output_path = f"./group_{group_id}.pdf"
    absolute_output_path = os.path.abspath(output_path)

    pdfkit.from_string(html_content, output_path, configuration=config)

    if not os.path.exists(absolute_output_path):
        return "Failed to create PDF file", 500

    return send_file(absolute_output_path, as_attachment=True, download_name=f'group_{group_id}.pdf')

def get_teacher_by_group(group_id):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.name, t.surname
        FROM Teachers t
        JOIN Courses c ON t.ID_Teacher = c.ID_Teacher
        WHERE c.ID_GROUP = ?
    """, (group_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {'name': row[0], 'surname': row[1]}
    return None

def generate_professor_pdf(professor_name):
    professor_details = get_professor_details(professor_name=professor_name)
    if not professor_details:
        return "No professor details found", 404

    html_content = f"""
    <html>
    <head>        
        <meta charset="UTF-8">
        <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            line-height: 1.6;
            color: #333;
        }}
        h1, h2 {{
            color: #2c3e50;
            border-bottom: 2px solid #2c3e50;
            padding-bottom: 10px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
            font-size: 0.9em;
            background-color: #f2f2f2;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px 15px;
            text-align: left;
        }}
        th {{
            background-color: #2980b9;
            color: white;
            text-transform: uppercase;
        }}
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        tr:hover {{
            background-color: #f1f1f1;
        }}
        </style>
    </head>
    <body>
        <h1>Professor {professor_name}</h1>
        <h2>Details</h2>
        <table>
            <thead>
                <tr>
                    <th>Name</th>
                    <th>Surname</th>
                    <th>Email</th>
                    <th>Subject</th>
                    <th>Availability</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>{professor_details['name']}</td>
                    <td>{professor_details['surname']}</td>
                    <td>{professor_details['email']}</td>
                    <td>{professor_details['subject']}</td>
                    <td>{professor_details['availability'].replace(",", ", ")}</td>
                </tr>
            </tbody>
        </table>
        <h2>Groups</h2>
        <table>
            <thead>
                <tr>
                    <th>Group</th>
                    <th>Day</th>
                    <th>Time</th>
                </tr>
            </thead>
            <tbody>
    """

    groups = get_professor_groups(professor_name)

    # Create a dictionary to store each group and its unique time slot
    group_dict = {}
    for group in groups:
        group_name = group[0]
        group_time = f"{group[1]} {group[2]}"
        group_dict[group_name] = group_time

    # Convert the dictionary to a list of unique groups with their times
    for group_name, group_time in group_dict.items():
        html_content += f"""
        <tr>
            <td>{group_name}</td>
            <td>{group_time.split()[0]}</td>
            <td>{group_time.split()[1]}</td>
        </tr>
        """

    html_content += """
            </tbody>
        </table>
    </body>
    </html>
    """

    pdf = pdfkit.from_string(html_content, False, configuration=config)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=professor_{professor_name}.pdf'
    return response

def get_groups_by_professor(professor_name):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    name_parts = professor_name.split()
    if len(name_parts) < 2:
        return []  # Nom de professeur invalide

    first_name = name_parts[0]
    last_name = name_parts[1]

    cursor.execute("""
        SELECT DISTINCT c.ID_GROUP, a.Day, a.Hour
        FROM Teachers t
        JOIN Courses c ON t.ID_Teacher = c.ID_Teacher
        JOIN List_Groups_Students lg ON c.ID_COURSE = lg.ID_COURSE
        JOIN Availability_Teachers at ON t.ID_Teacher = at.ID_Teacher
        JOIN Availabilities a ON at.ID_Availability = a.ID_Availability
        WHERE t.name = ? AND t.surname = ?
    """, (first_name, last_name))

    rows = cursor.fetchall()
    conn.close()

    groups = []
    for row in rows:
        groups.append({
            'group_id': row[0],
            'day': row[1],
            'time': row[2]
        })

    return groups

def get_professor_groups(professor_name):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    name_parts = professor_name.split()
    if len(name_parts) < 2:
        return []  # Nom de professeur invalide

    first_name = name_parts[0]
    last_name = name_parts[1]

    cursor.execute("""
        SELECT C.ID_GROUP, A.Day, A.Hour
        FROM Courses C
        JOIN Availabilities A ON C.ID_Availability = A.ID_Availability
        WHERE C.ID_Teacher = (
            SELECT ID_Teacher
            FROM Teachers
            WHERE name = ? AND surname = ?
        )
    """, (first_name, last_name))

    groups = cursor.fetchall()
    conn.close()

    return groups

if __name__ == '__main__':
    def open_browser():
        webbrowser.open_new('http://127.0.0.1:5000')

    threading.Timer(1, open_browser).start()
    app.run(debug=True)