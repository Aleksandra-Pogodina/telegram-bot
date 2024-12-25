import dataBase

def update_question_statistics(question_id, test_id, is_correct):
    """Обновляет статистику по вопросам в базе данных."""
    conn = dataBase.connect_db()
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
    conn = dataBase.connect_db()
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

def increment_started_count(test_id):
    """Увеличивает счетчик начавших тест."""
    conn = dataBase.connect_db()
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
    conn = dataBase.connect_db()
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
    conn = dataBase.connect_db()
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