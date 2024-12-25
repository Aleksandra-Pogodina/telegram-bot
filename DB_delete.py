import dataBase

def delete_question(question_id):
    """Удаляет вопрос из базы данных по заданному question_id и обновляет статистику."""
    conn = dataBase.connect_db()
    cursor = conn.cursor()

    # Удаляем связанные ответы
    cursor.execute("DELETE FROM answers WHERE question_id = ?", (question_id,))

    # Удаляем статистику вопроса
    cursor.execute("DELETE FROM question_statistics WHERE question_id = ?", (question_id,))

    # Удаляем сам вопрос
    cursor.execute("DELETE FROM questions WHERE question_id = ?", (question_id,))

    conn.commit()
    conn.close()

def delete_test(test_id):
    # Подключение к базе данных
    conn = dataBase.connect_db()
    cur = conn.cursor()

    try:
        # Удаляем все ответы, связанные с вопросами теста
        cur.execute('''
            DELETE FROM answers
            WHERE question_id IN (
                SELECT question_id FROM questions WHERE test_id = ?
            )
        ''', (test_id,))

        # Удаляем все вопросы, связанные с тестом
        cur.execute('''
            DELETE FROM questions
            WHERE test_id = ?
        ''', (test_id,))

        # Удаляем статистику для теста
        cur.execute('''
            DELETE FROM test_statistics
            WHERE test_id = ?
        ''', (test_id,))

        # Удаляем сам тест
        cur.execute('''
            DELETE FROM tests
            WHERE test_id = ?
        ''', (test_id,))

        # Фиксируем изменения
        conn.commit()

    except Exception as e:
        print(f"Произошла ошибка при удалении теста: {e}")

    finally:
        # Закрываем соединение с базой данных
        conn.commit()
        conn.close()