import sqlite3
import json
import os

DB_PATH = os.path.join("database", "expenses.db")

def init_db():
    if not os.path.exists("database"):
        os.makedirs("database")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            vendor TEXT,
            amount INTEGER,
            status TEXT DEFAULT 'PENDING',
            image_path TEXT NOT NULL,
            raw_text TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    print("✅ Đã khởi tạo Database thành công!")

def insert_expense(user_id, vendor, amount, image_path, raw_text_list):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # ensure_ascii=False giúp lưu tiếng Việt đúng định dạng, không bị lỗi font
    raw_text_json = json.dumps(raw_text_list, ensure_ascii=False)
    
    cursor.execute('''
        INSERT INTO expenses (user_id, vendor, amount, image_path, raw_text)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, vendor, amount, image_path, raw_text_json))
    
    last_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return last_id

if __name__ == "__main__":
    init_db()