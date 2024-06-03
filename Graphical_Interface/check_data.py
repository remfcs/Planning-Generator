import sqlite3

def verify_columns():
    conn = sqlite3.connect('test.sqlite3')
    cursor = conn.cursor()
    
    tables = ['Student', 'Teachers', 'List_Groups_Students']

    for table in tables:
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()
        print(f"Columns in {table}:")
        for column in columns:
            print(column)
        print("\n")

    conn.close()

if __name__ == "__main__":
    verify_columns()
