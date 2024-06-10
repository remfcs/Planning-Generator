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
from Export.export import generate_group_pdf, generate_professors_pdf, generate_professor_pdf, generate_group_csv, export_all_groups_csv, generate_professors_csv, generate_professor_csv, generate_group_excel, export_all_groups_excel, generate_professor_excel, export_all_professors_excel, get_student_details, export_all_groups

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
PROMO_AVAILABILITIES_PATH = os.path.join(UPLOAD_FOLDER, 'promo_availabilities.json')
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
    
    availability_Promo_json = request.form.get('availabilityPromo', '[]')
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
    elif file_type == 'excel':
        if export_all:
            return export_all_groups_excel()
        elif group_id:
            return generate_group_excel(group_id)
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
    elif file_type == 'excel':
        if export_all:
            return export_all_professors_excel()
        elif professor_name:
            return generate_professor_excel(professor_name)
        else:
            return "Missing professorId parameter", 400

    return "Invalid file type", 400

# Autres routes et fonctions...
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

@app.route('/deleteStudent', methods=['POST'])
def delete_student():
    data = request.get_json()
    email = data['email']
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
    return send_from_directory('.', 'Modify student/add-student.html')

@app.route('/export')
def export_page():
    return send_from_directory('Export', 'Export.html')

@app.route('/export.js')
def serve_export_js():
    return send_from_directory('Export', 'export.js')

@app.route('/groups')
def get_groups():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    query = "SELECT DISTINCT ID_COURSE FROM List_Groups_Students"
    cursor.execute(query)
    groups = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    return jsonify(groups)

@app.route('/api/professors', methods=['GET'])
def api_professors():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT T.name, T.surname, T.mail, T.Subject, 
               GROUP_CONCAT(DISTINCT A.Day || ' ' || A.Hour) as availabilities
        FROM Teachers T
        LEFT JOIN Availability_Teachers AT ON T.ID_Teacher = AT.ID_Teacher
        LEFT JOIN Availabilities A ON AT.ID_Availability = A.ID_Availability
        GROUP BY T.name, T.surname, T.mail, T.Subject
    """)
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


if __name__ == '__main__':
    def open_browser():
        webbrowser.open_new('http://127.0.0.1:5000')

    threading.Timer(1, open_browser).start()
    app.run(debug=True)
