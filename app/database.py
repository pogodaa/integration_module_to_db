import sqlite3
from typing import List, Optional
from .models import Record

class DatabaseManager:
    def __init__(self, db_path: str = "database.db"):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Получение соединения с БД"""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Создание таблицы при первом запуске"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    value REAL NOT NULL,
                    category TEXT NOT NULL,
                    description TEXT
                )
            ''')
            conn.commit()
    
    def add_record(self, record: Record) -> int:
        """Добавление записи (CREATE)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO records (name, value, category, description)
                VALUES (?, ?, ?, ?)
            ''', (record.name, record.value, record.category, record.description))
            conn.commit()
            return cursor.lastrowid
    
    def get_all_records(self) -> List[Record]:
        """Получение всех записей (READ)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, name, value, category, description FROM records')
            rows = cursor.fetchall()
            return [Record(id=row[0], name=row[1], value=row[2], category=row[3], description=row[4]) for row in rows]
    
    def get_record_by_id(self, record_id: int) -> Optional[Record]:
        """Получение записи по ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, name, value, category, description FROM records WHERE id = ?', (record_id,))
            row = cursor.fetchone()
            if row:
                return Record(id=row[0], name=row[1], value=row[2], category=row[3], description=row[4])
            return None
    
    def update_record(self, record: Record) -> bool:
        """Обновление записи (UPDATE)"""
        if record.id is None:
            return False
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE records 
                SET name = ?, value = ?, category = ?, description = ?
                WHERE id = ?
            ''', (record.name, record.value, record.category, record.description, record.id))
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_record(self, record_id: int) -> bool:
        """Удаление записи (DELETE)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM records WHERE id = ?', (record_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def search_records(self, query: str) -> List[Record]:
        """Поиск записей по имени или описанию"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, name, value, category, description 
                FROM records 
                WHERE name LIKE ? OR description LIKE ? OR category LIKE ?
            ''', (f'%{query}%', f'%{query}%', f'%{query}%'))
            rows = cursor.fetchall()
            return [Record(id=row[0], name=row[1], value=row[2], category=row[3], description=row[4]) for row in rows]