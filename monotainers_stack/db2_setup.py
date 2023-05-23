import os
import sqlite3
import json

def create_table(conn):
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lane_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lane_number INTEGER,
            lane_name TEXT,
            planogram_data TEXT,
            pending_data TEXT,
            realtime_data TEXT,
            processed_data TEXT
        )
    ''')

    conn.commit()


def insert_initial_data(conn):
    cursor = conn.cursor()

    # Initial data
    data = {
        "lane_number": 1,
        "lane_name": "NA",
        "planogram": {
            "in_stage": 0,
            "mapped": 0,
            "missing": 0,
            "total": 0,
            "trucks_required": 0,
            "trucks_ordered": 0
        },
        "pending": {
            "monotainers": [
                {"monotainer_id": "NA"}
            ],
            "total_monotainers": 1
        },
        "real_time_positions": [
            {
              "position": 8,
              "upper": {"monotainer_id": "NA", "misplaced": 0},
              "lower": {"monotainer_id": "NA", "misplaced": 0}
            },
            {
              "position": 7,
              "upper": {"monotainer_id": "NA", "misplaced": 0},
              "lower": {"monotainer_id": "NA", "misplaced": 0}
            },
            {
              "position": 6,
              "upper": {"monotainer_id": "NA", "misplaced": 0},
              "lower": {"monotainer_id": "NA", "misplaced": 0}
            },
            {
              "position": 5,
              "upper": {"monotainer_id": "NA", "misplaced": 0},
              "lower": {"monotainer_id": "NA", "misplaced": 0}
            },
            {
              "position": 4,
              "upper": {"monotainer_id": "NA", "misplaced": 0},
              "lower": {"monotainer_id": "NA", "misplaced": 0}
            },
            {
              "position": 3,
              "upper": {"monotainer_id": "NA", "misplaced": 0},
              "lower": {"monotainer_id": "NA", "misplaced": 0}
            },
            {
              "position": 2,
              "upper": {"monotainer_id": "NA", "misplaced": 0},
              "lower": {"monotainer_id": "NA", "misplaced": 0}
            },
            {
              "position": 1,
              "upper": {"monotainer_id": "NA", "misplaced": 0},
              "lower": {"monotainer_id": "NA", "misplaced": 0}
            }                                                                               
        ],
        "processed": {
            "monotainers": [
                {"monotainer_id": "NA"}
            ],
            "total_monotainers": 1
        }
    }

    cursor.execute('''
        INSERT INTO lane_data (lane_number, lane_name, planogram_data, pending_data, realtime_data, processed_data)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (data['lane_number'], data['lane_name'], json.dumps(data['planogram']), json.dumps(data['pending']), json.dumps(data['real_time_positions']), json.dumps(data['processed'])))

    conn.commit()

# def insert_initial_data(conn):
#     cursor = conn.cursor()
#     for i in range(1, 3):
#         cursor.execute('''
#             INSERT INTO lane_data (lane_number, lane_name, planogram_data, pending_data, realtime_data, processed_data)
#             VALUES (?, ?, ?, ?, ?, ?)
#         ''', (i, 'NA', 'NA', 'NA', 'NA', 'NA'))  # For lane 1 and lane 2
#     conn.commit()

def return_empty_positions():
  data = [
            {
              "position": 8,
              "upper": {"monotainer_id": "NA", "misplaced": 0},
              "lower": {"monotainer_id": "NA", "misplaced": 0}
            },
            {
              "position": 7,
              "upper": {"monotainer_id": "NA", "misplaced": 0},
              "lower": {"monotainer_id": "NA", "misplaced": 0}
            },
            {
              "position": 6,
              "upper": {"monotainer_id": "NA", "misplaced": 0},
              "lower": {"monotainer_id": "NA", "misplaced": 0}
            },
            {
              "position": 5,
              "upper": {"monotainer_id": "NA", "misplaced": 0},
              "lower": {"monotainer_id": "NA", "misplaced": 0}
            },
            {
              "position": 4,
              "upper": {"monotainer_id": "NA", "misplaced": 0},
              "lower": {"monotainer_id": "NA", "misplaced": 0}
            },
            {
              "position": 3,
              "upper": {"monotainer_id": "NA", "misplaced": 0},
              "lower": {"monotainer_id": "NA", "misplaced": 0}
            },
            {
              "position": 2,
              "upper": {"monotainer_id": "NA", "misplaced": 0},
              "lower": {"monotainer_id": "NA", "misplaced": 0}
            },
            {
              "position": 1,
              "upper": {"monotainer_id": "NA", "misplaced": 0},
              "lower": {"monotainer_id": "NA", "misplaced": 0}
            }                                                                               
        ]
  return data


def setup_database():
    if not os.path.exists("stack_memory2.db"):
        conn = sqlite3.connect("stack_memory2.db")
        create_table(conn)
        insert_initial_data(conn)
        conn.close()

if __name__ == "__main__":
    setup_database()
