import pdfkit
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
import pandas as pd  # Ajout de pandas pour l'export en Excel

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
        "teacher:": teachers
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
    SELECT s.NAME, s.SURNAME, s.EMAIL, s.SCHOOL_YEAR, lg.ID_COURSE, c.Language, t.NAME AS TeacherName, t.SURNAME AS TeacherSurname
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
        query += " AND s.SCHOOL_YEAR = ?"
        params.append(niveau)
    if professeur:
        query += " AND (t.NAME || ' ' || t.SURNAME) = ?"
        params.append(professeur)
    if langue:
        query += " AND c.Language = ?"
        params.append(langue)
    if group_lv1:
        query += " AND lg.ID_COURSE = ?"
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
    logging.debug(f"Retrieved students: {students}")
    return students

    conn.close()
    logging.debug(f"Retrieved students: {students}")
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
               GROUP_CONCAT(DISTINCT C.ID_COURSE || ' (' || A.Day || ' ' || A.Hour || ')') as groups
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
        return []

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    name_parts = professor_name.split()
    if len(name_parts) < 2:
        return []  # Nom de professeur invalide

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

    rows = cursor.fetchall()
    conn.close()

    professors = []
    for row in rows:
        professors.append({
            'name': row[0],
            'surname': row[1],
            'email': row[2],
            'subject': row[3],
            'availability': row[4]
        })

    return professors

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
    
    query = "SELECT DISTINCT ID_COURSE FROM List_Groups_Students"
    cursor.execute(query)
    groups = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    return jsonify(groups)

@app.route('/groups/<promo>/<language>')
def get_courses_by_promo(promo, language):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    query = """
    SELECT ID_COURSE, COUNT(*) AS student_count 
    FROM List_Groups_Students 
    WHERE ID_COURSE LIKE ? 
    GROUP BY ID_COURSE
    """
    cursor.execute(query, ('%' + language,))
    courses_with_count = cursor.fetchall()
    filtered_courses = []
    for course in courses_with_count:
        course_id = course[0]
        start = course_id.find('{') + 1
        end = course_id.find('}')
        if start > 0 and end > start:
            promos = course_id[start:end].split(', ')
            if promo in promos:
                filtered_courses.append({'course_id': course_id, 'student_count': course[1]})
    conn.close()
    return jsonify(filtered_courses)

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
    cursor.execute("""
        INSERT INTO Student (EMAIL, NAME, SURNAME, SCHOOL_YEAR, LV1, LV2, REDUCED_EXAM)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, new_student)
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

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
    return send_from_directory('.', 'Modify student/add-student.html')

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
        html_content += f"""
        <h2>Group {group_id}</h2>
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
        if groups:
            groups_list = groups.split(',')
            unique_groups = list(dict.fromkeys(groups_list))
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
               GROUP_CONCAT(DISTINCT C.ID_COURSE || ' (' || A.Day || ' ' || A.Hour || ')') as groups
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
        availability = availability.replace(",", ", ") if availability else ""
        if groups:
            groups_list = groups.split(',')
            unique_groups = list(dict.fromkeys(groups_list))
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
            day = student.get('Day', 'Unknown')  # Modify this if 'Day' is not included in student details
            time = student.get('Hour', 'Unknown')  # Modify this if 'Hour' is not included in student details
            writer.writerow([group, student['Surname'], student['Name'], student['Email'], student['Class'], student['GROUP_LV1'], student['Language'], teacher_name, teacher_surname, day, time])

    output.seek(0)
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=all_groups.csv'
    response.headers['Content-Type'] = 'text/csv'
    return response

def generate_group_excel(group_id):
    students = get_student_details(group_lv1=group_id)
    df = pd.DataFrame(students)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Group Data')
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = f'attachment; filename=group_{group_id}.xlsx'
    response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    return response

def export_all_groups_excel():
    response = get_groups()
    if response.status_code != 200:
        logging.error(f"Failed to get groups: {response.status_code}")
        return "Failed to get groups", 500

    groups = response.get_json()
    if not groups:
        logging.error("No groups found")
        return "No groups found", 400

    all_data = []
    for group in groups:
        students = get_student_details(group_lv1=group)
        for student in students:
            all_data.append([group] + list(student.values()))

    df = pd.DataFrame(all_data, columns=["GroupID", "Surname", "Name", "Email", "Class", "GROUP_LV1", "Language", "TeacherName", "TeacherSurname"])
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='All Groups Data')
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=all_groups.xlsx'
    response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    return response

def generate_professor_csv(professor_name):
    professor_details = get_professor_details(professor_name=professor_name)
    if not professor_details:
        return "No professor details found", 404
    
    groups = get_professor_groups(professor_name)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Name", "Surname", "Email", "Subject", "Availability", "Groups"])
    
    for detail in professor_details:
        name, surname, email, subject, availability = detail
        group_details = "; ".join([f"{group[0]} ({group[1]} {group[2]})" for group in groups])
        writer.writerow([name, surname, email, subject, availability, group_details])
    
    output.seek(0)
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = f'attachment; filename=professor_{professor_name}.csv'
    response.headers['Content-Type'] = 'text/csv'
    return response

def generate_professor_excel(professor_name):
    professors = get_professor_details(professor_name=professor_name)
    if not professors:
        return "No professor details found", 404
    
    df = pd.DataFrame(professors)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Professor Data')
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = f'attachment; filename=professor_{professor_name}.xlsx'
    response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    return response

def export_all_professors_excel():
    professors = get_professors()
    df = pd.DataFrame(professors, columns=["Name", "Surname", "Email", "Subject", "Availability"])
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Professors Data')
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=professors_list.xlsx'
    response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    return response

def generate_group_pdf(group_id):
    students = get_student_details(group_lv1=group_id)
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
        <h1>Group {group_id}</h1>
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

def generate_professor_pdf(professor_name):
    professor_details = get_professor_details(professor_name=professor_name)
    if not professor_details:
        return "No professor details found", 404

    html_content = f"""
    <html>
    <head>
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
    """
    for detail in professor_details:
        html_content += f"""
        <tr>
            <td>{detail['name']}</td>
            <td>{detail['surname']}</td>
            <td>{detail['email']}</td>
            <td>{detail['subject']}</td>
            <td>{detail['availability'].replace(",", ", ")}</td>
        </tr>
        """
    html_content += """
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
    for group in groups:
        html_content += f"""
        <tr>
            <td>{group[0]}</td>
            <td>{group[1]}</td>
            <td>{group[2]}</td>
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
        SELECT DISTINCT lg.ID_COURSE, a.Day, a.Hour
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

    cursor.execute("""
        SELECT c.ID_COURSE, a.Day, a.Hour
        FROM Courses c
        JOIN Teachers t ON c.ID_Teacher = t.ID_Teacher
        JOIN Availabilities a ON c.ID_Availability = a.ID_Availability
        WHERE t.name || ' ' || t.surname = ?
    """, (professor_name,))

    groups = cursor.fetchall()
    conn.close()

    return groups

if __name__ == '__main__':
    def open_browser():
        webbrowser.open_new('http://127.0.0.1:5000')

    threading.Timer(1, open_browser).start()
    app.run(debug=True)
