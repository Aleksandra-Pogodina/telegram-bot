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

def save_test_time(test_id, time):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE tests SET time = ? WHERE test_id = ?", (time, test_id))
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

def get_test_time(test_id):
    """Возвращает время теста по test_id из базы данных."""
    conn = connect_db()  # Подключение к базе данных
    cursor = conn.cursor()
    cursor.execute("SELECT time FROM tests WHERE test_id = ?", (test_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0]  # Возвращаем значение времени
    else:
        return None  # Если тест не найден, возвращаем None


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

def get_correct_answers_by_question_id(question_id):
    """Возвращает список правильных ответов для данного вопроса по его ID."""
    conn = connect_db()
    cursor = conn.cursor()

    # SQL-запрос для получения всех правильных ответов
    cursor.execute("SELECT answer_text FROM answers WHERE question_id = ? AND is_correct = 1", (question_id,))
    correct_answers = cursor.fetchall()  # Извлекаем все строки результата

    conn.close()

    return [answer[0] for answer in correct_answers]  # Возвращаем список текстов правильных ответов


def is_correct_answer(answer):
    conn = connect_db()
    cursor = conn.cursor()

    # Получаем запись ответа по ID
    cursor.execute("SELECT is_correct FROM answers WHERE answer_id = ?", (answer,))
    result = cursor.fetchone()  # Извлекаем первую строку результата

    conn.close()

    # Если результат найден и он правильный, возвращаем True, иначе False
    return result[0] if result else False


def update_question_statistics(question_id, test_id, is_correct):
    """Обновляет статистику по вопросам в базе данных."""
    conn = connect_db()
    cursor = conn.cursor()

    # Проверяем, существует ли запись для данного вопроса и теста
    cursor.execute("SELECT total_attempts, correct_attempts FROM question_statistics WHERE question_id = ? AND test_id = ?", (question_id, test_id))
    result = cursor.fetchone()

    if result:
        total_attempts, correct_attempts = result
        total_attempts += 1
        if is_correct:
            correct_attempts += 1
        cursor.execute("UPDATE question_statistics SET total_attempts = ?, correct_attempts = ? WHERE question_id = ? AND test_id = ?", (total_attempts, correct_attempts, question_id, test_id))
    else:
        # Если записи нет, создаём новую
        total_attempts = 1
        correct_attempts = 1 if is_correct else 0
        cursor.execute("INSERT INTO question_statistics (question_id, test_id, total_attempts, correct_attempts) VALUES (?, ?, ?, ?)", (question_id, test_id, total_attempts, correct_attempts))

    conn.commit()
    conn.close()


def get_test_statistics(test_id):
    """Возвращает статистику по вопросам для данного теста."""
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            question_id,
            (correct_attempts * 100.0 / total_attempts) AS success_rate
        FROM 
            question_statistics
        WHERE 
            test_id = ?
    """, (test_id,))

    statistics = cursor.fetchall()
    conn.close()

    return statistics

def get_test_title_by_id(test_id):
    """Возвращает название теста по его ID."""
    conn = connect_db()  # Подключение к базе данных
    cursor = conn.cursor()

    # SQL-запрос для получения названия теста
    cursor.execute("SELECT title FROM tests WHERE test_id = ?", (test_id,))
    result = cursor.fetchone()  # Извлекаем первую строку результата

    conn.close()  # Закрываем соединение

    if result:
        return result[0]  # Возвращаем название теста
    else:
        return None  # Если тест не найден, возвращаем None

def increment_started_count(test_id):
    """Увеличивает счетчик начавших тест."""
    conn = connect_db()
    cursor = conn.cursor()

    # Проверяем, существует ли запись для данного теста
    cursor.execute("SELECT started_count FROM test_statistics WHERE test_id = ?", (test_id,))
    result = cursor.fetchone()

    if result:
        # Если запись существует, увеличиваем счетчик
        new_started_count = result[0] + 1
        cursor.execute("UPDATE test_statistics SET started_count = ? WHERE test_id = ?", (new_started_count, test_id))
    else:
        # Если записи нет, создаем новую с начальным значением 1
        cursor.execute("INSERT INTO test_statistics (test_id, started_count) VALUES (?, ?)", (test_id, 1))

    conn.commit()
    conn.close()

def increment_completed_count(test_id):
    """Увеличивает счетчик завершивших тест."""
    conn = connect_db()
    cursor = conn.cursor()

    # Проверяем, существует ли запись для данного теста
    cursor.execute("SELECT completed_count FROM test_statistics WHERE test_id = ?", (test_id,))
    result = cursor.fetchone()

    if result:
        # Если запись существует, увеличиваем счетчик
        new_completed_count = result[0] + 1
        cursor.execute("UPDATE test_statistics SET completed_count = ? WHERE test_id = ?", (new_completed_count, test_id))
    else:
        # Если записи нет, создаем новую с начальным значением 1
        cursor.execute("INSERT INTO test_statistics (test_id, completed_count) VALUES (?, ?)", (test_id, 1))

    conn.commit()
    conn.close()


def get_test_statistics_pie(test_id):
    """Возвращает статистику по количеству начавших и завершивших тест."""
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT started_count, completed_count FROM test_statistics WHERE test_id = ?", (test_id,))
    result = cursor.fetchone()

    conn.close()

    if result:
        started_count, completed_count = result
        completion_rate = (completed_count / started_count * 100) if started_count > 0 else 0
        return {
            'started': started_count,
            'completed': completed_count,
            'completion_rate': completion_rate
        }

    return None  # Если статистика не найдена


def get_user_tests(user_id):
    """Возвращает список тестов, созданных пользователем."""
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT test_id, title FROM tests WHERE user_id = ?", (user_id,))
    tests = cursor.fetchall()  # Получаем все тесты

    conn.close()
    return tests  # Возвращаем список кортежей (test_id, title)


def get_test_info(test_id):
    """Возвращает информацию о тесте: название, количество вопросов и время на вопрос."""
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT title, time FROM tests WHERE test_id = ?", (test_id,))
    test_info = cursor.fetchone()

    cursor.execute("SELECT COUNT(*) FROM questions WHERE test_id = ?", (test_id,))
    question_count = cursor.fetchone()[0]

    conn.close()

    return test_info, question_count  # Возвращаем кортеж (информация о тесте, количество вопросов)





def get_started_count(test_id):
    """Возвращает количество пользователей, которые начали тест."""
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT started_count FROM test_statistics WHERE test_id = ?", (test_id,))
    result = cursor.fetchone()

    conn.close()
    return result[0] if result else 0


def get_completed_count(test_id):
    """Возвращает количество пользователей, которые завершили тест."""
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT completed_count FROM test_statistics WHERE test_id = ?", (test_id,))
    result = cursor.fetchone()

    conn.close()
    return result[0] if result else 0

def get_answered_count(question_id):
    """Возвращает количество пользователей, ответивших на вопрос."""
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT total_attempts FROM question_statistics WHERE question_id = ?", (question_id,))
    result = cursor.fetchone()

    conn.close()
    return result[0] if result else 0


def get_correct_answered_count(question_id):
    """Возвращает количество пользователей, ответивших верно на вопрос."""
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT correct_attempts FROM question_statistics WHERE question_id = ?", (question_id,))
    result = cursor.fetchone()

    conn.close()
    return result[0] if result else 0

