import dataBase

def update_test_title(test_id, new_title):
    """Обновляет название теста в базе данных по заданному test_id."""
    conn = dataBase.connect_db()
    cursor = conn.cursor()

    cursor.execute("UPDATE tests SET title = ? WHERE test_id = ?", (new_title, test_id))
    conn.commit()
    conn.close()

def update_test_description(test_id, new_description):
    """Обновляет описание теста в базе данных по заданному test_id."""
    conn = dataBase.connect_db()
    cursor = conn.cursor()

    cursor.execute("UPDATE tests SET description = ? WHERE test_id = ?", (new_description, test_id))
    conn.commit()
    conn.close()

def update_test_time(test_id, timer):
    """Обновляет время на прохождение теста в базе данных по заданному test_id."""
    conn = dataBase.connect_db()
    cursor = conn.cursor()

    cursor.execute("UPDATE tests SET time = ? WHERE test_id = ?", (timer, test_id))
    conn.commit()
    conn.close()