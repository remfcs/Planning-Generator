from flask import Flask, request, jsonify, render_template
import sqlite3

app = Flask(__name__)

DATABASE = 'database.sqlite3'

def get_db():
    try:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return None

@app.route('/')
def index():
    return render_template('add-student.html')

@app.route('/get-courses', methods=['GET'])
def get_courses():
    promo = request.args.get('promo')
    language = request.args.get('language')
    print(f"Received request for promo: {promo}, language: {language}")
    conn = get_db()
    if conn:
        cursor = conn.cursor()
        try:
            query = "SELECT ID_COURSE FROM Courses WHERE PROMO LIKE ? AND LANGUAGE = ?"
            cursor.execute(query, (f'%{promo}%', language))
            courses = cursor.fetchall()
            print(f"Courses found: {courses}")
            return jsonify([dict(course) for course in courses])
        except sqlite3.Error as e:
            print(f"SQL error: {e}")
            return jsonify({'error': 'SQL error'}), 500
    else:
        return jsonify({'error': 'Database connection failed'}), 500

@app.route('/add-student', methods=['POST'])
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
    
    conn = get_db()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO Student (EMAIL, NAME, SURNAME, SCHOOL_YEAR, LV1, LV2, REDUCED_EXAM)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, new_student)
            conn.commit()
            return jsonify({'success': True})
        except sqlite3.Error as e:
            print(f"SQL error: {e}")
            return jsonify({'error': 'SQL error'}), 500
    else:
        return jsonify({'error': 'Database connection failed'}), 500

if __name__ == '__main__':
    app.run(debug=True)
