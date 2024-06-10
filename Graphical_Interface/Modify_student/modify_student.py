import sqlite3
import logging
from flask import jsonify

DATABASE_PATH = './data/database.sqlite3'

def add_student(data):
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

def add_list(data_english):
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

def add_list2(data_lv2):
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

def delete_student(data):
    email = data['email']
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Student WHERE EMAIL = ?", (email,))
    cursor.execute("DELETE FROM List_Groups_Students WHERE ID_STUDENT = ?", (email,))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})
