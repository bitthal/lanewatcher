import os
import sqlite3

def create_tables(conn):
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS planogram (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lane_number INTEGER,
            lane_name TEXT,
            in_staged INTEGER,
            mapped INTEGER,
            missing INTEGER,
            total INTEGER,
            trucks_required INTEGER,
            trucks_ordered INTEGER
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pending (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lane_number INTEGER,
            pending_id TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS processed (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lane_number INTEGER,
            processed_id TEXT
        )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS real_time_positions (
        position INTEGER,
        lane_number INTEGER,
        upper_lane1 TEXT,
        lower_lane1 TEXT,
        upper_lane2 TEXT,
        lower_lane2 TEXT,
        PRIMARY KEY(position, lane_number)
        )
    ''')

    conn.commit()

def insert_initial_data(conn):
    cursor = conn.cursor()
    for i in range(8, 0, -1):
        cursor.execute('''
            INSERT INTO real_time_positions (position, lane_number, upper_lane1, lower_lane1, upper_lane2, lower_lane2)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (i, 1, 'NA', 'NA', 'NA', 'NA'))  # For lane 1
        cursor.execute('''
            INSERT INTO real_time_positions (position, lane_number, upper_lane1, lower_lane1, upper_lane2, lower_lane2)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (i, 2, 'NA', 'NA', 'NA', 'NA'))  # For lane 2
    conn.commit()

def setup_database():
    if not os.path.exists("stack_memory.db"):
        conn = sqlite3.connect("stack_memory.db")
        create_tables(conn)
        insert_initial_data(conn)
        conn.close()

if __name__ == "__main__":
    setup_database()
