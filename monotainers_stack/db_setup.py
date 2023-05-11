import os
import sqlite3

def create_table(conn):
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stack_memory (
            position INTEGER PRIMARY KEY,
            upper_lane1 TEXT,
            lower_lane1 TEXT,
            upper_lane2 TEXT,
            lower_lane2 TEXT
        )
    """)
    conn.commit()

def insert_initial_data(conn):
    cursor = conn.cursor()
    for i in range(8, 0, -1):
        cursor.execute("""
            INSERT INTO stack_memory (position, upper_lane1, lower_lane1, upper_lane2, lower_lane2)
            VALUES (?, ?, ?, ?, ?)
        """, (i, 'NA', 'NA', 'NA', 'NA'))
    conn.commit()

def setup_database():
    if not os.path.exists("stack_memory.db"):
        conn = sqlite3.connect("stack_memory.db")
        create_table(conn)
        insert_initial_data(conn)
        conn.close()

if __name__ == "__main__":
    setup_database()
