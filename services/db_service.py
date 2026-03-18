import sqlite3
import json
import os
import pandas as pd  


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


def update_status(expense_id, new_status):
    """Cập nhật trạng thái duyệt (Task W2-3.3)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('UPDATE expenses SET status = ? WHERE id = ?', (new_status, expense_id))
    conn.commit()
    conn.close()
    print(f"✅ Đã cập nhật ID {expense_id} sang {new_status}")


def export_to_excel():
    """Xuất file Excel báo cáo (Task W2-3.3)"""
    conn = sqlite3.connect(DB_PATH)
    # Nguyệt yêu cầu chỉ xuất những cái đã APPROVED
    query = "SELECT * FROM expenses WHERE status = 'APPROVED'"
    df = pd.read_sql_query(query, conn)
    conn.close()


    if df.empty:
        print("⚠️ Không có dữ liệu nào được APPROVED để xuất.")
        return None


    report_name = "report_bizbot.xlsx"
    df.to_excel(report_name, index=False)
    print(f"🚀 Xuất file thành công: {report_name}")
    return report_name






if __name__ == "__main__":
    init_db()
    export_to_excel()


# Test thử
if __name__ == "__main__":
    init_db()
    
   
