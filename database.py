import sqlite3

conn = sqlite3.connect("users.db")
cursor = conn.cursor()


cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fullname TEXT,
    student_group TEXT,
    phone TEXT,
    ariza_text TEXT
)
""")

conn = sqlite3.connect("users.db")
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS message_links (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        group_message_id INTEGER
    )
""")
conn.commit()
conn.close()



async def save_message_link(user_id, group_message_id):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO message_links (user_id, group_message_id) VALUES (?, ?)", (user_id, group_message_id))
    conn.commit()
    conn.close()

async def get_user_by_group_message(group_message_id):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM message_links WHERE group_message_id = ?", (group_message_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None


async def insert_user(fullname, group, phone, ariza_text):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO users (fullname, student_group, phone, ariza_text)
    VALUES (?, ?, ?, ?)
    """, (fullname, group, phone, ariza_text))

    conn.commit()
    conn.close()



async def get_user_by_phone(phone):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id FROM users
        WHERE phone = ?
        ORDER BY id DESC
        LIMIT 1
    """, (phone,))

    row = cursor.fetchone()
    conn.close()

    # Faqat ID qaytadi (agar topilmasa None)
    return row[0] if row else None


# --- 4. Barcha foydalanuvchilarni olish ---
async def get_all_users():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users")
    data = cursor.fetchall()

    conn.close()
    return data
