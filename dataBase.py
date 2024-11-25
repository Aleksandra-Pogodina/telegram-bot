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


    cur.execute('''CREATE TABLE IF NOT EXISTS statistics (
                    statistic_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    test_id INTEGER,
                    correct_answers BOOLEAN,
                    total_questions INTEGER,
                    FOREIGN KEY (user_id) REFERENCES users(user_id))''')

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
    cursor.execute("INSERT INTO tests (user_id, title, description) VALUES (?, ?, ?)",
                   (user_id, title, description))
    test_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return test_id

def save_link(link, test_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE tests SET link = ? WHERE test_id = ?", (link, test_id))
    conn.commit()
    conn.close()

def save_question(test_id, question_text, tip):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO questions (test_id, question_text, tip) VALUES (?, ?, ?)",
                   (test_id, question_text, tip))
    question_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return question_id


def count_answers_by_question_id(question_id):
    """Возвращает количество ответов для данного вопроса по его ID."""
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM answers WHERE question_id = ?", (question_id,))
    count = cursor.fetchone()[0]  # Получаем первое значение из результата запроса

    conn.close()

    return count


def save_answer(question_id, answer_text, is_correct):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO answers (question_id, answer_text, is_correct) VALUES (?, ?, ?)",
                   (question_id, answer_text, is_correct))
    conn.commit()
    conn.close()


def test_exists(test_id):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM tests WHERE test_id = ?", (test_id,))
    exists = cursor.fetchone()[0] > 0

    conn.close()
    return exists


def get_question_ids_by_test_id(test_id):
    """Возвращает список идентификаторов вопросов для данного теста."""
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT question_id FROM questions WHERE test_id = ?", (test_id,))
    question_ids = [row[0] for row in cursor.fetchall()]  # Извлекаем все ID вопросов

    conn.close()

    return question_ids


def get_questions_by_test_id(test_id):
    """Получает все вопросы по ID теста."""
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM questions WHERE test_id = ?", (test_id,))
    questions = cursor.fetchall()  # Получаем все вопросы

    conn.close()

    return questions


def get_answers_by_question_id(question_id):
    """Получает все ответы по ID вопроса."""
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM answers WHERE question_id = ?", (question_id,))
    answers = cursor.fetchall()  # Получаем все ответы

    conn.close()

    return answers


def get_correct_answer_by_question_id(question_id):
    """Возвращает правильный ответ для данного вопроса по его ID."""
    conn = connect_db()
    cursor = conn.cursor()

    # SQL-запрос для получения правильного ответа
    cursor.execute("SELECT answer_text FROM answers WHERE question_id = ? AND is_correct = 1", (question_id,))
    correct_answer = cursor.fetchone()  # Извлекаем первую строку результата

    conn.close()

    return correct_answer[0] if correct_answer else None


def is_correct_answer(answer):
    conn = connect_db()
    cursor = conn.cursor()

    # Получаем запись ответа по ID
    cursor.execute("SELECT is_correct FROM answers WHERE answer_id = ?", (answer,))
    result = cursor.fetchone()  # Извлекаем первую строку результата

    conn.close()

    # Если результат найден и он правильный, возвращаем True, иначе False
    return result[0] if result else False


def save_statistics(user_id, test_id, correct_answers, total_questions):
    """Сохраняет статистику прохождения теста в базе данных."""
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("INSERT INTO statistics (user_id, test_id, correct_answers, total_questions) VALUES (?, ?, ?, ?)",
                   (user_id, test_id, correct_answers, total_questions))

    conn.commit()
    conn.close()