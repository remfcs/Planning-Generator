import sqlite3
from flask import Flask, jsonify, request, send_from_directory
import threading
import webbrowser
import os

app = Flask(__name__, static_url_path='', static_folder='.')

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'test.sqlite3')

def get_student_details(name=None, niveau=None, professeur=None, langue=None, group_lv1=None):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    query = """
    SELECT s.NAME, s.SURNAME, s.EMAIL, s.SCHOOL_YEAR, lg.ID_COURSE, c.Language, t.NAME AS TeacherName, t.SURNAME AS TeacherSurname
    FROM Student s
    LEFT JOIN List_Groups_Students lg ON s.EMAIL = lg.ID_STUDENT
    LEFT JOIN Courses c ON lg.ID_COURSE = c.ID_GROUP
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

# Route pour servir le fichier HTML des professeurs
@app.route('/professors')
def serve_professors_html():
    return send_from_directory('.', 'professors.html')

# Routes pour servir les fichiers statiques
@app.route('/script.js')
def serve_script_js():
    return send_from_directory('.', 'script.js')

@app.route('/professors.js')
def serve_professors_js():
    return send_from_directory('.', 'professors.js')

@app.route('/style.css')
def serve_style_css():
    return send_from_directory('.', 'style.css')

@app.route('/home.html')
def serve_home_html():
    return send_from_directory('.', 'home.html')

if __name__ == '__main__':
    def open_browser():
        webbrowser.open_new('http://127.0.0.1:5000')

    threading.Timer(1, open_browser).start()
    app.run(debug=True)
