from flask import Flask, request, jsonify, send_from_directory
import sqlite3
import os
import webbrowser
import threading
import time

app = Flask(__name__)

# Define the path to the SQLite database file
DATABASE = os.path.join(os.path.dirname(__file__), 'test.sqlite3')

def query_db(query, args=(), one=False):
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    conn.close()
    return (rv[0] if rv else None) if one else rv

def open_browser():
    time.sleep(1)  # Attendre une seconde pour s'assurer que le serveur a démarré
    webbrowser.open('http://127.0.0.1:5000/')


@app.route('/')
def index():
    return send_from_directory('.', 'home.html')

@app.route('/style.css')
def style():
    return send_from_directory('.', 'style.css')

@app.route('/script.js')
def script():
    return send_from_directory('.', 'script.js')

@app.route('/students', methods=['GET'])
def get_students():
    name = request.args.get('name', '').lower()
    niveau = request.args.get('niveau', '')
    professeur = request.args.get('professeur', '')
    langue = request.args.get('langue', '')

    query = """
        SELECT s.NAME, s.SURNAME, s.EMAIL, s.SCHOOL_YEAR, s.LV1, s.GROUP_LV1, t.NAME AS TEACHER_NAME, t.SURNAME AS TEACHER_SURNAME
        FROM Student s
        LEFT JOIN Teachers t ON s.EMAIL = t.MAIL
        WHERE 1=1
    """
    filters = []
    
    if name:
        query += " AND LOWER(s.NAME) LIKE ?"
        filters.append(f"%{name}%")
    if niveau:
        query += " AND s.SCHOOL_YEAR = ?"
        filters.append(niveau)
    if professeur:
        query += " AND (t.NAME || ' ' || t.SURNAME) = ?"
        filters.append(professeur)
    if langue:
        query += " AND s.LV1 = ?"
        filters.append(langue)
    
    students = query_db(query, filters)
    
    student_list = []
    for student in students:
        student_list.append({
            "Name": student[0],
            "Surname": student[1],
            "Email": student[2],
            "Class": student[3],
            "LV1": student[4],
            "GROUP_LV1": student[5],
            "TeacherName": student[6],
            "TeacherSurname": student[7]
        })
    
    return jsonify(student_list)

@app.route('/professors', methods=['GET'])
def get_professors():
    professors = query_db("SELECT DISTINCT NAME || ' ' || SURNAME AS FULL_NAME FROM Teachers")
    return jsonify([prof[0] for prof in professors])

@app.route('/languages', methods=['GET'])
def get_languages():
    languages = query_db("SELECT DISTINCT LV1 FROM Student")
    return jsonify([lang[0] for lang in languages])

if __name__ == '__main__':
    threading.Thread(target=open_browser).start()
    app.run(debug=True)
