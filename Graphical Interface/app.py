from flask import Flask, jsonify, request
import sqlite3

app = Flask(__name__)

def connect_db():
    conn = sqlite3.connect('data_copy.sqlite3')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/students', methods=['GET'])
def get_students():
    name = request.args.get('name')
    conn = connect_db()
    cursor = conn.cursor()
    
    if name:
        cursor.execute("SELECT * FROM students WHERE name LIKE ?", ('%' + name + '%',))
    else:
        cursor.execute("SELECT * FROM students")
        
    students = cursor.fetchall()
    conn.close()
    
    student_list = [dict(row) for row in students]
    return jsonify(student_list)

if __name__ == '__main__':
    app.run(debug=True)
