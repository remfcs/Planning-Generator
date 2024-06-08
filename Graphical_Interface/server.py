import sqlite3
from flask import Flask, jsonify, request, send_from_directory
import threading
import webbrowser
import os
import subprocess
import json

app = Flask(__name__, static_url_path='', static_folder='.')

# Définir le dossier de téléchargement
UPLOAD_FOLDER = '././data/uploads'
UPLOAD_FOLDER_LEVEL = '././data/uploads/input_level'
UPLOAD_FOLDER_INFO = '././data/uploads/input_info'
TEACHERS_JSON_PATH = os.path.join(UPLOAD_FOLDER, 'teachers.json')
DATABASE_PATH = './data/database.sqlite3'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOAD_FOLDER_INFO'] = UPLOAD_FOLDER_INFO
app.config['UPLOAD_FOLDER_LEVEL'] = UPLOAD_FOLDER_LEVEL

# Créer le dossier de téléchargement s'il n'existe pas
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(UPLOAD_FOLDER_LEVEL):
    os.makedirs(UPLOAD_FOLDER_LEVEL)
if not os.path.exists(UPLOAD_FOLDER_INFO):
    os.makedirs(UPLOAD_FOLDER_INFO)

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

# Afficher les données pour vérification (peut être remplacé par une autre logique)
    response_data = {
    "estimation": f"Estimation du nombre de nouveaux étudiants: {estimate_number_student}",
    "halfday_slots": f"Nombre de demi-journées: {halfday_slot}",
    "students_files": ", ".join(saved_files['students_files']),
    "level_files": ", ".join(saved_files['level_files']),
    "teacher:": teachers
    }
    try:
        # Exécuter le script main.py
        result = subprocess.run(['python', '././main.py'], capture_output=True, text=True)
        
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
        result = subprocess.run(['python', '././main.py'], capture_output=True, text=True)
        
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
    # Récupérer les informations des professeurs avec la disponibilité combinée
    cursor.execute("""
        SELECT T.name, T.surname, T.mail, T.Subject, 
               GROUP_CONCAT(A.Day || ' ' || A.Hour) as availabilities
        FROM Teachers T
        LEFT JOIN Availability_Teachers AT ON T.ID_Teacher = AT.ID_Teacher
        LEFT JOIN Availabilities A ON AT.ID_Availability = A.ID_Availability
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

@app.route('/api/professor_details', methods=['GET'])
def get_professor_details():
    professor_name = request.args.get('professor')
    if not professor_name:
        return jsonify([])

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Séparez le prénom et le nom du professeur
    name_parts = professor_name.split()
    if len(name_parts) < 2:
        return jsonify([])  # Nom de professeur invalide

    first_name = name_parts[0]
    last_name = name_parts[1]

    # Récupérer les langues et les groupes enseignés par le professeur
    cursor.execute("""
        SELECT DISTINCT c.Language, lg.ID_COURSE
        FROM Teachers t
        JOIN Courses c ON t.ID_Teacher = c.ID_Teacher
        JOIN List_Groups_Students lg ON c.ID_COURSE = lg.ID_COURSE
        WHERE t.name = ? AND t.surname = ?
    """, (first_name, last_name))

    rows = cursor.fetchall()
    conn.close()

    languages = list(set(row[0] for row in rows))
    groups = list(set(row[1] for row in rows))

    return jsonify({
        'languages': languages,
        'groups': groups
    })

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
        # Extract the part inside the braces {}
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

# Route pour servir le fichier HTML des professeurs
@app.route('/professors')
def serve_professors_html():
    return send_from_directory('.', 'professors.html')

# Routes pour servir les fichiers statiques
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

# Ajouter la route pour servir la page Export.html
@app.route('/export')
def serve_export_html():
    return send_from_directory('.', './Export/export.html')

if __name__ == '__main__':
    def open_browser():
        webbrowser.open_new('http://127.0.0.1:5000')

    threading.Timer(1, open_browser).start()
    app.run(debug=True)
