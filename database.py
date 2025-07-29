# database.py
import sqlite3
from datetime import datetime

class DatabaseManager:
    """負責所有資料庫操作的管理類別"""
    def __init__(self, db_name="time_tracker.db"):
        """初始化資料庫連接並創建資料表"""
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        """如果資料表不存在，則創建它"""
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
        """插入一個新的事件紀錄，只包含開始時間，並返回該紀錄的ID"""
        self.cursor.execute('''
            INSERT INTO events (event_name, description, start_time)
            VALUES (?, ?, ?)
        ''', (event_name, description, start_time))
        self.conn.commit()
        return self.cursor.lastrowid

    def update_event_end_time(self, event_id, end_time):
        """根據ID更新事件的結束時間"""
        self.cursor.execute('''
            UPDATE events
            SET end_time = ?
            WHERE id = ?
        ''', (end_time, event_id))
        self.conn.commit()

    def get_all_events(self):
        """獲取所有事件紀錄，按開始時間降序排列"""
        self.cursor.execute("SELECT * FROM events ORDER BY start_time DESC")
        return self.cursor.fetchall()

    def delete_event(self, event_id):
        """根據ID刪除一個事件紀錄"""
        self.cursor.execute("DELETE FROM events WHERE id = ?", (event_id,))
        self.conn.commit()

    def close(self):
        """關閉資料庫連接"""
        self.conn.close()