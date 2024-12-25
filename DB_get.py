import dataBase

def count_answers_by_question_id(question_id):
    """Возвращает количество ответов для данного вопроса по его ID."""
    conn = dataBase.connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM answers WHERE question_id = ?", (question_id,))
    count = cursor.fetchone()[0]  # Получаем первое значение из результата запроса

    conn.close()

    return count


def test_exists(test_id):
    conn = dataBase.connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM tests WHERE test_id = ?", (test_id,))
    exists = cursor.fetchone()[0] > 0

    conn.close()
    return exists


def get_question_ids_by_test_id(test_id):
    """Возвращает список идентификаторов вопросов для данного теста."""
    conn = dataBase.connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT question_id FROM questions WHERE test_id = ?", (test_id,))
    question_ids = [row[0] for row in cursor.fetchall()]  # Извлекаем все ID вопросов

    conn.close()

    return question_ids


def get_questions_by_test_id(test_id):
    """Получает все вопросы по ID теста."""
    conn = dataBase.connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM questions WHERE test_id = ?", (test_id,))
    questions = cursor.fetchall()  # Получаем все вопросы

    conn.close()

    return questions

def get_test_time(test_id):
    """Возвращает время теста по test_id из базы данных."""
    conn = dataBase.connect_db()  # Подключение к базе данных
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
    conn = dataBase.connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM answers WHERE question_id = ?", (question_id,))
    answers = cursor.fetchall()  # Получаем все ответы

    conn.close()

    return answers


def get_correct_answer_by_question_id(question_id):
    """Возвращает правильный ответ для данного вопроса по его ID."""
    conn = dataBase.connect_db()
    cursor = conn.cursor()

    # SQL-запрос для получения правильного ответа
    cursor.execute("SELECT answer_text FROM answers WHERE question_id = ? AND is_correct = 1", (question_id,))
    correct_answer = cursor.fetchone()  # Извлекаем первую строку результата

    conn.close()

    return correct_answer[0] if correct_answer else None

def get_correct_answers_by_question_id(question_id):
    """Возвращает список правильных ответов для данного вопроса по его ID."""
    conn = dataBase.connect_db()
    cursor = conn.cursor()

    # SQL-запрос для получения всех правильных ответов
    cursor.execute("SELECT answer_text FROM answers WHERE question_id = ? AND is_correct = 1", (question_id,))
    correct_answers = cursor.fetchall()  # Извлекаем все строки результата

    conn.close()

    return [answer[0] for answer in correct_answers]  # Возвращаем список текстов правильных ответов


def is_correct_answer(answer):
    conn = dataBase.connect_db()
    cursor = conn.cursor()

    # Получаем запись ответа по ID
    cursor.execute("SELECT is_correct FROM answers WHERE answer_id = ?", (answer,))
    result = cursor.fetchone()  # Извлекаем первую строку результата

    conn.close()

    # Если результат найден и он правильный, возвращаем True, иначе False
    return result[0] if result else False

def get_test_title_by_id(test_id):
    """Возвращает название теста по его ID."""
    conn = dataBase.connect_db()  # Подключение к базе данных
    cursor = conn.cursor()

    # SQL-запрос для получения названия теста
    cursor.execute("SELECT title FROM tests WHERE test_id = ?", (test_id,))
    result = cursor.fetchone()  # Извлекаем первую строку результата

    conn.close()  # Закрываем соединение

    if result:
        return result[0]  # Возвращаем название теста
    else:
        return None  # Если тест не найден, возвращаем None

def get_user_tests(user_id):
    """Возвращает список тестов, созданных пользователем."""
    conn = dataBase.connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT test_id, title FROM tests WHERE user_id = ?", (user_id,))
    tests = cursor.fetchall()  # Получаем все тесты

    conn.close()
    return tests  # Возвращаем список кортежей (test_id, title)


def get_test_info(test_id):
    """Возвращает информацию о тесте: название, количество вопросов и время на вопрос."""
    conn = dataBase.connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT title, time, description, link FROM tests WHERE test_id = ?", (test_id,))
    test_info = cursor.fetchone()

    cursor.execute("SELECT COUNT(*) FROM questions WHERE test_id = ?", (test_id,))
    question_count = cursor.fetchone()[0]

    conn.close()

    return test_info, question_count  # Возвращаем кортеж (информация о тесте, количество вопросов)


def get_started_count(test_id):
    """Возвращает количество пользователей, которые начали тест."""
    conn = dataBase.connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT started_count FROM test_statistics WHERE test_id = ?", (test_id,))
    result = cursor.fetchone()

    conn.close()
    return result[0] if result else 0


def get_completed_count(test_id):
    """Возвращает количество пользователей, которые завершили тест."""
    conn = dataBase.connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT completed_count FROM test_statistics WHERE test_id = ?", (test_id,))
    result = cursor.fetchone()

    conn.close()
    return result[0] if result else 0

def get_answered_count(question_id):
    """Возвращает количество пользователей, ответивших на вопрос."""
    conn = dataBase.connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT total_attempts FROM question_statistics WHERE question_id = ?", (question_id,))
    result = cursor.fetchone()

    conn.close()
    return result[0] if result else 0


def get_correct_answered_count(question_id):
    """Возвращает количество пользователей, ответивших верно на вопрос."""
    conn = dataBase.connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT correct_attempts FROM question_statistics WHERE question_id = ?", (question_id,))
    result = cursor.fetchone()

    conn.close()
    return result[0] if result else 0