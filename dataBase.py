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
                link TEXT,
                time INTEGER,
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


    cur.execute('''CREATE TABLE IF NOT EXISTS question_statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_id INTEGER,
                test_id INTEGER,
                total_attempts INTEGER DEFAULT 0,
                correct_attempts INTEGER DEFAULT 0,
                FOREIGN KEY (question_id) REFERENCES questions(question_id),
                FOREIGN KEY (test_id) REFERENCES tests(test_id));''')

    cur.execute('''CREATE TABLE IF NOT EXISTS test_statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                test_id INTEGER,
                started_count INTEGER DEFAULT 0,
                completed_count INTEGER DEFAULT 0,
                FOREIGN KEY (test_id) REFERENCES tests(test_id));''')


    conn.commit()
    cur.close()
    conn.close()






