import sqlite3

def connect_db():
    return sqlite3.connect('tests.sql')

def create_tables():
    conn = connect_db()
    cur = conn.cursor()

    cur.execute('''CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY)''')

    cur.execute('''CREATE TABLE IF NOT EXISTS tests (
                test_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                title TEXT,
                description TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id))''')


    cur.execute('''CREATE TABLE IF NOT EXISTS questions (
                question_id INTEGER PRIMARY KEY AUTOINCREMENT,
                test_id INTEGER,
                question_text TEXT,
                tip TEXT,
                FOREIGN KEY (test_id) REFERENCES tests(test_id))''')


    cur.execute('''CREATE TABLE IF NOT EXISTS answers (
                answer_id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_id INTEGER,
                answer_text TEXT,
                is_correct BOOLEAN,
                FOREIGN KEY (question_id) REFERENCES questions(question_id))''')

    conn.commit()
    cur.close()
    conn.close()

def add_user(user_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()

def save_test(user_id, title, description):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tests (user_id, title, description) VALUES (?, ?, ?)", (user_id, title, description))
    test_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return test_id

def save_question(test_id, question_text, tip):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO questions (test_id, question_text, tip) VALUES (?, ?, ?)",
                   (test_id, question_text, tip))
    question_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return question_id


def save_answer(question_id, answer_text, is_correct):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO answers (question_id, answer_text, is_correct) VALUES (?, ?, ?)",
                   (question_id, answer_text, is_correct))
    conn.commit()
    conn.close()