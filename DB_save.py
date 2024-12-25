import dataBase

def add_user(user_id):
    conn = dataBase.connect_db()
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()

def save_test(user_id, title, description):
    conn = dataBase.connect_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tests (user_id, title, description) VALUES (?, ?, ?)",
                   (user_id, title, description))
    test_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return test_id

def save_link(link, test_id):
    conn = dataBase.connect_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE tests SET link = ? WHERE test_id = ?", (link, test_id))
    conn.commit()
    conn.close()

def save_test_time(test_id, time):
    conn = dataBase.connect_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE tests SET time = ? WHERE test_id = ?", (time, test_id))
    conn.commit()
    conn.close()

def save_question(test_id, question_text, tip):
    conn = dataBase.connect_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO questions (test_id, question_text, tip) VALUES (?, ?, ?)",
                   (test_id, question_text, tip))
    question_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return question_id

def save_answer(question_id, answer_text, is_correct):
    conn = dataBase.connect_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO answers (question_id, answer_text, is_correct) VALUES (?, ?, ?)",
                   (question_id, answer_text, is_correct))
    conn.commit()
    conn.close()