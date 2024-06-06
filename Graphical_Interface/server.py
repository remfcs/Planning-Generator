import sqlite3
from flask import Flask, jsonify, request, send_from_directory
import threading
import webbrowser
import os

app = Flask(__name__, static_url_path='', static_folder='.')

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'database.sqlite3')

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
    professors = get_professors()
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
    query = "SELECT DISTINCT ID_COURSE FROM List_Groups_Students WHERE ID_COURSE LIKE ?"
    cursor.execute(query, ('%_' + language,))
    courses = cursor.fetchall()
    filtered_courses = []
    for course in courses:
        course_id = course[0]
        # Extract the part inside the braces {}
        start = course_id.find('{') + 1
        end = course_id.find('}')
        if start > 0 and end > start:
            promos = course_id[start:end].split(', ')
            if promo in promos:
                filtered_courses.append(course_id)
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

@app.route('/add2', methods=['POST'])
def add_list():
    data_english = request.get_json()
    new_student = (
        data_english['course'],
        data_english['email']
    )
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO List_Groups_Students (ID_COURSE, ID_STUDENT)
        VALUES (?, ?)
        """, new_student)
    conn.commit()
    conn.close()

@app.route('/add3', methods=['POST'])
def add_list2():
    data_lv2 = request.get_json()
    new_student = (
        data_lv2['course'],
        data_lv2['email']
    )
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO List_Groups_Students (ID_COURSE, ID_STUDENT)
        VALUES (?, ?)
        """, new_student)
    conn.close()

@app.route('/timeslot')
def get_timeslot():
    course = request.args.get('course') 
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT ID_AVAILABILITY FROM Courses WHERE ID_COURSE LIKE ?", (course,))
    timeslot = cursor.fetchone()
    conn.close()
    return jsonify(timeslot[0])

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

if __name__ == '__main__':
    def open_browser():
        webbrowser.open_new('http://127.0.0.1:5000')

    threading.Timer(1, open_browser).start()
    app.run(debug=True)