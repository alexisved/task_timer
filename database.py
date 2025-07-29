# database.py
import sqlite3
from datetime import datetime

class DatabaseManager:
    """負責所有資料庫操作的管理類別"""
    def __init__(self, db_name="time_tracker.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_name TEXT NOT NULL,
                description TEXT,
                start_time TEXT NOT NULL,
                end_time TEXT
            )
        ''')
        self.conn.commit()

    def insert_event(self, event_name, description, start_time):
        self.cursor.execute('''
            INSERT INTO events (event_name, description, start_time)
            VALUES (?, ?, ?)
        ''', (event_name, description, start_time))
        self.conn.commit()
        return self.cursor.lastrowid

    def update_event_end_time(self, event_id, end_time):
        self.cursor.execute('''
            UPDATE events
            SET end_time = ?
            WHERE id = ?
        ''', (end_time, event_id))
        self.conn.commit()

    def search_events(self, start_date=None, end_date=None, name_query=None, desc_query=None):
        """
        根據多個條件動態搜尋事件。
        - 日期格式應為 'YYYY-MM-DD'
        - name_query 和 desc_query 為模糊搜尋
        """
        query = "SELECT * FROM events"
        conditions = []
        params = []

        if start_date:
            conditions.append("DATE(start_time) >= ?")
            params.append(start_date)
        
        if end_date:
            conditions.append("DATE(start_time) <= ?")
            params.append(end_date)
            
        if name_query:
            conditions.append("event_name LIKE ?")
            params.append(f"%{name_query}%")

        if desc_query:
            conditions.append("description LIKE ?")
            params.append(f"%{desc_query}%")

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY start_time DESC"
        
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def delete_event(self, event_id):
        self.cursor.execute("DELETE FROM events WHERE id = ?", (event_id,))
        self.conn.commit()

    def close(self):
        self.conn.close()