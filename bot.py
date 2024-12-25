
from telebot import types
import dataBase as db
import matplotlib
matplotlib.use('Agg')  # Используем бэкенд Agg
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from openpyxl.utils import get_column_letter
import DB_update
import DB_statistic
import DB_get
import DB_save
import DB_delete


db.create_tables()


class TestBot:
    def __init__(self, bot):
        self.bot = bot
        self.current_test_title = None
        self.current_test_id = None
        self.current_question_id = None
        self.current_question = None
        self.current_type = None
        self.link = None
        self.user_answers = []
        self.correct_answers_from_user = 0
        self.current_question_index = 0
        self.clock = 10
        self.questions = []
        self.timer = None
        self.question_type = None
        self.correct = None
        self.question_data = None
        self.edit = None
        self.description = None

    def start(self):

        @self.bot.message_handler(commands=['start'])
        def handle_start(message):
            if ' ' in message.text:
                s = message.text.split(' ')
                test_id = s[-1]
                start_test(message, test_id)

            else:
                markup = types.InlineKeyboardMarkup()
                btn1 = types.InlineKeyboardButton("Создать тест", callback_data='create_test')
                btn2 = types.InlineKeyboardButton("Мои тесты", callback_data='my_tests')
                btn3 = types.InlineKeyboardButton("О боте", callback_data='about_bot')
                btn4 = types.InlineKeyboardButton("Загрузить тест в txt формате", callback_data="txt")
                markup.row(btn1, btn2)
                markup.row(btn3)
                markup.row(btn4)
                self.bot.send_message(message.chat.id, 'Добро пожаловать!', reply_markup=markup)

        @self.bot.callback_query_handler(func=lambda call: True)
        def on_click(call):
            if call.data.startswith('test_'):
                test_id = int(call.data.split('_')[1])
                about_test(call.message, test_id)
            elif call.data.startswith('edit_test_'):
                test_id = int(call.data.split('_')[2])
                edit_menu(call.message, test_id)
            elif call.data.startswith('statistics_'):
                test_id = int(call.data.split('_')[1])
                view_statistics(call.message, test_id)
            elif call.data.startswith('statisticsexcel_'):
                test_id = int(call.data.split('_')[1])
                send_excel(call.message, test_id)
            elif call.data.startswith('editTitle_'):
                test_id = int(call.data.split('_')[1])
                edit_title(call.message, test_id)
            elif call.data.startswith('editDescription_'):
                test_id = int(call.data.split('_')[1])
                edit_description(call.message, test_id)
            elif call.data.startswith('editTimer_'):
                test_id = int(call.data.split('_')[1])
                edit_timer(call.message, test_id)
            elif call.data.startswith('time_'):
                timer = int(call.data.split('_')[1])
                test_id = int(call.data.split('_')[2])
                save_new_time(call.message, timer, test_id)
            elif call.data.startswith('editQuestion_'):
                self.edit = None
                test_id = int(call.data.split('_')[1])
                edit_question(call.message, test_id)
            elif call.data.startswith("addQuestion_"):
                self.current_test_id = int(call.data.split('_')[1])
                self.edit = True
                type_question(call.message)
            elif call.data.startswith("delQuestion_"):
                test_id = int(call.data.split('_')[1])
                choose_question_to_delete(call.message, test_id)
            elif call.data.startswith("question_"):
                question_id = int(call.data.split('_')[1])
                test_id = int(call.data.split('_')[2])
                delete_question(call.message, question_id, test_id)
            elif call.data.startswith('goTest_'):
                test_id = int(call.data.split('_')[1])
                start_test(call.message, test_id)
            elif call.data.startswith("deleteTest_"):
                test_id = int(call.data.split('_')[1])
                delete_test(call.message, test_id)
            else:
                if call.data == "create_test":
                    handle_test(call.message)
                elif call.data == "my_tests":
                    handle_my_tests(call.message)
                elif call.data == "about_bot":
                    handle_about_bot(call.message)
                elif call.data == "txt":
                    send_template(call.message)
                elif call.data == 'skip_description':
                    skip_description(call.message)
                elif call.data == "input_disc":
                    save_description(call.message)
                elif call.data == "10":
                    self.clock = 10
                    save_time(call.message)
                elif call.data == "30":
                    self.clock = 30
                    save_time(call.message)
                elif call.data == "1":
                    self.clock = 60
                    save_time(call.message)
                elif call.data == "vvod":
                    save_type_question(call.message, "vvod")
                elif call.data == "one":
                    save_type_question(call.message, "one")
                elif call.data == "several":
                    save_type_question(call.message, "several")
                elif call.data == 'add_answer':
                    make_answer(call.message)
                elif call.data == 'make_question':
                    type_question(call.message)
                elif call.data == 'done':
                    done_test(call.message)
                elif call.data == 'take_test':
                    start_test(call.message, self.current_test_id)

        @self.bot.message_handler(commands=['txt_test'])
        def send_template(message):
            # Отправляем текстовое сообщение перед документом
            self.bot.send_message(chat_id=message.chat.id,
                             text="Вот шаблон для Вашего теста. \nОтправьте в таком же формате Ваш тест, в документе формата txt")

            # Отправляем файл пользователю
            with open('test_template.txt', 'rb') as file:
                self.bot.send_document(chat_id=message.chat.id, document=file)

        @self.bot.message_handler(content_types=['document'])
        def handle_document(message):
            DB_save.add_user(message.chat.id)

            # Проверяем, является ли загружаемый файл текстовым
            if message.document.mime_type == 'text/plain':
                file_info = self.bot.get_file(message.document.file_id)
                downloaded_file = self.bot.download_file(file_info.file_path)

                # Сохраняем загруженный файл
                with open('uploaded_test.txt', 'wb') as new_file:
                    new_file.write(downloaded_file)

                # Обрабатываем файл
                process_test_file(message, 'uploaded_test.txt')


        def process_test_file(message, file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()

            for line in lines[0:3]:
                line = line.strip()
                if not line:
                    continue

                # Обработка заголовка теста
                if line.startswith("Название:"):
                    self.current_test_title = line[len("Название:"):].strip()  # Заголовок теста
                    continue

                # Обработка описания теста
                if line.startswith("Описание:"):
                    self.description = line[len("Описание:"):].strip()  # Описание теста
                    continue

                # Обработка времени теста
                if line.startswith("Время:"):
                    self.clock = int(line[len("Время:"):].strip())  # Время на тест
                    continue

            # Сохраняем тест в базе данных
            self.current_test_id = DB_save.save_test(message.chat.id, self.current_test_title, self.description)
            self.link = f"https://t.me/TheCreatorOfTheTestsBot?start={self.current_test_id}"
            DB_save.save_link(self.link, self.current_test_id)
            DB_save.save_test_time(self.current_test_id, self.clock)

            # Инициализация переменных
            current_question = {}

            for line in lines[3:]:
                line = line.strip()
                if not line:
                    continue  # Пропускаем пустые строки

                # Обработка вопроса
                if line.startswith("Вопрос:"):
                    if current_question:  # Если текущий вопрос уже существует, сохраняем его
                        save_question_to_db(current_question)

                    current_question = {'question': line[len("Вопрос:"):].strip()}  # Получаем текст вопроса
                    continue

                # Обработка типа вопроса
                if line.startswith("Тип:"):
                    if line[len("Тип:"):].strip() == "ввод":
                        current_question['type'] = "vvod"
                    elif line[len("Тип:"):].strip() == "несколько":
                        current_question['type'] = "several"
                    elif line[len("Тип:"):].strip() == "один":
                        current_question['type'] = "one"
                    continue

                # Обработка вариантов ответов
                if line.startswith("Варианты:"):
                    options = line[len("Варианты:"):].strip().split(',')
                    current_question['options'] = [option.strip() for option in options]

                    # Определяем правильные ответы как все варианты, заключенные в кавычки
                    current_question['correct'] = [option.strip()[1:-1] for option in current_question['options'] if
                                                   option.startswith('"') and option.endswith('"')]

                    continue

            # Сохраняем последний вопрос после завершения цикла (если есть)
            if current_question:
                save_question_to_db(current_question)

            done_test(message)

        def save_question_to_db(current_question):
            current_question_id = DB_save.save_question(self.current_test_id, current_question['question'],
                                                   current_question['type'])

            # Сохраняем варианты ответов, если они есть
            if 'options' in current_question:
                for option in current_question['options']:
                    # Убираем кавычки при сохранении в БД
                    option_to_save = option.strip().replace('"', '')
                    is_correct = option_to_save in current_question['correct']
                    DB_save.save_answer(current_question_id, option_to_save.lower(), is_correct=is_correct)

        @self.bot.message_handler(commands=['create_test'])
        def handle_test(message):
            DB_save.add_user(message.chat.id)
            self.bot.send_message(message.chat.id, "Введите название теста.")
            self.bot.register_next_step_handler(message, save_test_title)

        def save_test_title(message):
            self.current_test_title = message.text

            markup = types.InlineKeyboardMarkup()
            skip_button = types.InlineKeyboardButton("Пропустить", callback_data='skip_description')
            input_button = types.InlineKeyboardButton("Ввести описание", callback_data='input_disc')
            markup.add(skip_button, input_button)
            self.bot.send_message(message.chat.id, 'Вы можете добавить описание к тесту, а можете пропустить этот шаг',
                             reply_markup=markup)

        def skip_description(message):
            user_id = message.chat.id
            self.current_test_id = DB_save.save_test(user_id, self.current_test_title, None)

            self.bot.send_message(message.chat.id, f"Тест '{self.current_test_title}' создан без описания.")
            save_link(message)

        def save_description(message):
            self.bot.send_message(message.chat.id, "Введите описание:")
            self.bot.register_next_step_handler(message, save_description_in_db)

        def save_description_in_db(message):
            description = message.text
            self.current_test_id = DB_save.save_test(message.from_user.id, self.current_test_title, description)
            self.bot.send_message(message.chat.id, f"Тест '{self.current_test_title}' с описанием '{description}' создан!")
            save_link(message)

        def save_link(message):
            t_id = self.current_test_id
            self.link = f"https://t.me/TheCreatorOfTheTestsBot?start={t_id}"
            DB_save.save_link(self.link, self.current_test_id)
            clock(message)

        def clock(message):
            markup = types.InlineKeyboardMarkup()
            ten_button = types.InlineKeyboardButton("10с", callback_data="10")
            three_button = types.InlineKeyboardButton("30с", callback_data='30')
            min_button = types.InlineKeyboardButton("1м", callback_data='1')
            markup.row(ten_button, three_button, min_button)
            self.bot.send_message(message.chat.id,
                             'Сколько времени будет отводиться на один вопрос: 10 секунд, 30 секунд или 1 минута?',
                             reply_markup=markup)

        def save_time(message):
            t_id = self.current_test_id
            DB_save.save_test_time(t_id, self.clock)
            type_question(message)

        def type_question(message):
            markup = types.InlineKeyboardMarkup()
            one_button = types.InlineKeyboardButton("один правильный ответ", callback_data="one")
            several_button = types.InlineKeyboardButton("несколько правильных ответов", callback_data='several')
            vvod_button = types.InlineKeyboardButton("ввод с клавиатуры", callback_data='vvod')
            markup.add(one_button)
            markup.add(several_button)
            markup.add(vvod_button)
            self.bot.send_message(message.chat.id,
                             'Вы можете создать вопрос с вариантами ответа, а можете сделать ввод ответа пользователем',
                             reply_markup=markup)

        def save_type_question(message, tip):
            self.current_type = tip
            save_question(message)

        def save_question(message):
            self.bot.send_message(message.chat.id, 'Введите вопрос.')
            self.bot.register_next_step_handler(message, save_question_in_db)

        def save_question_in_db(message):
            self.current_question = message.text
            self.current_question_id = DB_save.save_question(self.current_test_id, self.current_question, self.current_type)

            self.bot.send_message(message.chat.id, "Вопрос сохранен.")
            make_answer(message)

        def make_answer(message):
            self.bot.send_message(message.chat.id, "Введите вариант ответа:")
            self.bot.register_next_step_handler(message, save_answer)

        def save_answer(message):
            if self.current_type == "vvod":
                save_answer_in_db(message, message.text)
            else:
                answer_text = message.text

                markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
                markup.add('Да', 'Нет')
                self.bot.send_message(message.chat.id, "Это правильный ответ?", reply_markup=markup)

                self.bot.register_next_step_handler(message, lambda m: save_answer_in_db(m, answer_text))

        def save_answer_in_db(message, answer_text="да"):
            if message.text.lower() == 'да' or self.current_type == "vvod":
                is_correct = True
            else:
                is_correct = False

            DB_save.save_answer(self.current_question_id, answer_text, is_correct)
            count = DB_get.count_answers_by_question_id(self.current_question_id)

            if self.current_type != "vvod" and count < 2:
                markup = types.InlineKeyboardMarkup()
                button1 = types.InlineKeyboardButton("Добавить вариант ответа", callback_data='add_answer')
                markup.row(button1)
                self.bot.send_message(message.chat.id, "Вариант ответа сохранен. Добавьте ещё вариант ответа для теста",
                                 reply_markup=markup)
            elif self.current_type != "vvod":
                if self.edit:
                    markup = types.InlineKeyboardMarkup()
                    button1 = types.InlineKeyboardButton("Добавить вариант ответа", callback_data='add_answer')
                    button2 = types.InlineKeyboardButton("Закончить создание вопроса",
                                                         callback_data=f'editQuestion_{self.current_test_id}')
                    markup.row(button1)
                    markup.row(button2)
                    self.bot.send_message(message.chat.id,
                                     "Вариант ответа сохранен. Вы можете добавить еще один вариант ответа или закончить создание вопроса.",
                                     reply_markup=markup)
                else:
                    markup = types.InlineKeyboardMarkup()
                    button1 = types.InlineKeyboardButton("Добавить вариант ответа", callback_data='add_answer')
                    button2 = types.InlineKeyboardButton("Создать вопрос", callback_data='make_question')
                    button3 = types.InlineKeyboardButton("Закончить создание теста", callback_data='done')
                    markup.row(button1)
                    markup.row(button2)
                    markup.row(button3)
                    self.bot.send_message(message.chat.id,
                                     "Вариант ответа сохранен. Вы можете добавить еще один вариант ответа или создать ещё вопрос или закончить создание теста.",
                                     reply_markup=markup)
            elif self.current_type == "vvod":
                if self.edit:
                    markup = types.InlineKeyboardMarkup()
                    button1 = types.InlineKeyboardButton("Закончить создание вопроса",
                                                         callback_data=f'editQuestion_{self.current_test_id}')
                    markup.row(button1)
                    self.bot.send_message(message.chat.id,
                                     "Вариант ответа сохранен. Вы можете закончить создание вопроса.",
                                     reply_markup=markup)
                else:
                    markup = types.InlineKeyboardMarkup()
                    button2 = types.InlineKeyboardButton("Создать вопрос", callback_data='make_question')
                    button3 = types.InlineKeyboardButton("Закончить создание теста", callback_data='done')
                    markup.row(button2)
                    markup.row(button3)
                    self.bot.send_message(message.chat.id,
                                     "Вариант ответа сохранен. Вы можете создать ещё вопрос или закончить создание теста.",
                                     reply_markup=markup)

        def done_test(message):
            markup = types.InlineKeyboardMarkup()
            take_test_button = types.InlineKeyboardButton("Пройти тест", callback_data='take_test')
            markup.add(take_test_button)

            t_id = self.current_test_id
            self.bot.send_message(
                message.chat.id,
                f"Тест сохранён\nСсылка на тест: <a href='https://t.me/TheCreatorOfTheTestsBot?start={t_id}'>https://t.me/TheCreatorOfTheTestsBot?start={t_id}</a>",
                parse_mode='HTML',
                reply_markup=markup
            )

        def get_correct_answer_indices(option_texts, correct_answers):
            correct_indices = []
            for answer in correct_answers:
                if answer in option_texts:
                    index = option_texts.index(answer)
                    correct_indices.append(index)
            return correct_indices

        def start_test(message, test_id):
            self.current_question_index = 0
            self.correct_answers_from_user = 0
            self.correct = None
            self.question_data = None
            self.clock = DB_get.get_test_time(test_id)
            if DB_get.test_exists(test_id):
                #test_time = DB_get.get_test_time(test_id)
                test_title = DB_get.get_test_title_by_id(test_id)
                self.bot.send_message(message.chat.id, f"Вы начали тест {test_title}")
                DB_statistic.increment_started_count(test_id)
                self.questions = DB_get.get_questions_by_test_id(test_id)
                send_question(message, test_id)
            else:
                self.bot.send_message(message.chat.id, "Такого теста не существует")

        def send_question(message, test_id):
            length = len(self.questions)

            if self.current_question_index < length:

                self.question_data = self.questions[self.current_question_index]
                question_text = self.question_data[2]
                self.question_type = self.question_data[3]

                if self.question_type == "one":
                    options = DB_get.get_answers_by_question_id(self.question_data[0])
                    self.option_texts = [option[2] for option in options]

                    self.correct = DB_get.get_correct_answer_by_question_id(self.question_data[0])

                    if self.correct in self.option_texts:
                        correct_id = self.option_texts.index(self.correct)

                    self.current_question_index += 1

                    self.bot.send_poll(message.chat.id, question_text, self.option_texts, allows_multiple_answers=False,
                                  type='quiz', correct_option_id=correct_id, open_period=self.clock, is_anonymous=False)


                elif self.question_type == "several":
                    options = DB_get.get_answers_by_question_id(self.question_data[0])
                    self.option_texts = [option[2] for option in options]

                    self.correct = DB_get.get_correct_answers_by_question_id(self.question_data[0])

                    self.current_question_index += 1

                    self.bot.send_poll(message.chat.id, question_text, self.option_texts, allows_multiple_answers=True,
                                  type="regular", open_period=self.clock, is_anonymous=False)


                elif self.question_type == "vvod":
                    self.bot.send_message(message.chat.id, question_text)
                    self.bot.register_next_step_handler_by_chat_id(message.chat.id, handle_text_answer, test_id)

                @self.bot.poll_answer_handler()
                def handle_poll_answer(poll_answer):
                    if self.question_type == "several":
                        correct_indices = get_correct_answer_indices(self.option_texts, self.correct)

                        # Преобразуем списки в множества для удобства сравнения
                        user_answers_set = set(poll_answer.option_ids)
                        correct_answers_set = set(correct_indices)

                        if user_answers_set == correct_answers_set:
                            DB_statistic.update_question_statistics(self.question_data[0], test_id, True)
                            self.correct_answers_from_user += 1
                            self.bot.send_message(message.chat.id, "Все ответы правильные!")
                        else:
                            DB_statistic.update_question_statistics(self.question_data[0], test_id, False)
                            self.bot.send_message(message.chat.id,
                                             f"Неверно. Правильные ответы: {', '.join(self.correct)}")

                        send_question(message, test_id)

                    elif self.question_type == "one":
                        if self.option_texts[poll_answer.option_ids[0]] == self.correct:
                            DB_statistic.update_question_statistics(self.question_data[0], test_id, True)
                            self.correct_answers_from_user += 1
                        else:
                            DB_statistic.update_question_statistics(self.question_data[0], test_id, False)
                            self.bot.send_message(message.chat.id,
                                             f"Неверно. Правильный ответ: {self.correct}")

                        send_question(message, test_id)

            else:
                DB_statistic.increment_completed_count(test_id)
                statistic_for_user(message, length)

        def handle_text_answer(message, test_id):
            self.correct = DB_get.get_correct_answer_by_question_id(self.question_data[0])
            if message.text.lower() == self.correct.lower():
                DB_statistic.update_question_statistics(self.question_data[0], test_id, True)
                self.bot.send_message(message.chat.id, "Правильный ответ")
                self.correct_answers_from_user += 1
            else:
                DB_statistic.update_question_statistics(self.question_data[0], test_id, False)
                self.bot.send_message(message.chat.id, f"Неверно. Правильный ответ: {self.correct.lower()}")

            self.current_question_index += 1
            send_question(message, test_id)

        def statistic_for_user(message, total):
            percent = round((self.correct_answers_from_user / total) * 100, 2)
            self.bot.send_message(message.chat.id,
                                  f"Вы ответили верно на {self.correct_answers_from_user} из {total} вопросов.\n"
                                  f"Таким образом, Вы ответили верно на {percent}% вопросов.")

        def create_histogram(statistics, test_title):
            """Создает гистограмму успешности вопросов."""
            labels = []
            success_rates = []

            for index, (question_id, success_rate) in enumerate(statistics):
                labels.append(f"Вопрос {index + 1}")  # Нумерация вопросов от 1
                success_rates.append(success_rate)

            plt.figure(figsize=(10, 6))
            bars = plt.bar(labels, success_rates, color='orange')

            plt.ylabel('Процент успешности (%)')
            plt.title(f"Статистика успешности по тесту: {test_title}", pad=40)  # Увеличиваем отступ заголовка
            plt.xticks(rotation=45)  # Поворачиваем метки по оси X для лучшей читаемости
            plt.ylim(0, 100)  # Устанавливаем пределы по оси Y от 0 до 100

            # Добавляем проценты на столбиках
            for bar in bars:
                yval = bar.get_height()  # Высота столбика
                plt.text(bar.get_x() + bar.get_width() / 2, yval - 5, f'{yval:.1f}%', ha='center',
                         va='top')  # Сдвигаем текст вниз

            # Сохраняем гистограмму в файл
            chart_filename = "test_statistics_histogram.png"
            plt.tight_layout()  # Автоматически подгоняем размеры графика
            plt.savefig(chart_filename)
            plt.close()  # Закрываем фигуру, чтобы не занимать память

            return chart_filename

        def view_statistics(message, test_id):
            statistics = DB_statistic.get_test_statistics(test_id)

            if not statistics:
                markup = types.InlineKeyboardMarkup()
                button = types.InlineKeyboardButton("<< Назад к меню теста", callback_data=f'test_{test_id}')
                markup.add(button)
                self.bot.send_message(message.chat.id, "Нет доступной статистики для этого теста.", reply_markup=markup)
                return

            test_title = DB_get.get_test_title_by_id(test_id)

            # Создаем круговую диаграмму
            chart_filename = create_histogram(statistics, test_title)

            # Отправляем изображение пользователю
            with open(chart_filename, 'rb') as chart_file:
                self.bot.send_photo(message.chat.id, chart_file)

            show_test_statistics(message, test_id)

        def create_test_statistics_pie_chart(started_count, completed_count, test_title):
            """Создает круговую диаграмму статистики по тесту."""
            labels = []
            sizes = []

            # Определяем, какие данные добавлять
            if completed_count > 0:
                labels.append('Завершили тест')
                sizes.append(completed_count)

            if started_count - completed_count > 0:
                labels.append('Не завершили тест')
                sizes.append(started_count - completed_count)

            # Проверяем, есть ли данные для отображения
            if not sizes:
                print("Нет данных для отображения.")
                return None  # Или можно вернуть какое-то значение по умолчанию

            colors = ['orange', 'grey']  # Цвета для завершивших и не завершивших
            plt.figure(figsize=(8, 8))

            wedges, texts, autotexts = plt.pie(sizes, labels=labels, colors=colors, autopct='', startangle=140)
            plt.axis('equal')  # Равные оси для круга
            plt.title(f"Статистика по тесту: {test_title}", pad=20)

            total = started_count  # Общее количество участников теста
            if total == 0:
                plt.text(0, 0, 'Нет участников', ha='center', va='center', fontsize=20)
            else:
                for i, wedge in enumerate(wedges):
                    count = sizes[i]
                    percentage = count / total * 100 if total > 0 else 0

                    # Если один из секторов равен нулю, выводим текст в центре
                    if count == 0:
                        plt.text(0, 0, f'{total} (0.0%)', ha='center', va='center', fontsize=20)
                    else:
                        angle = (wedge.theta2 + wedge.theta1) / 2.0  # Находим угол для размещения текста
                        x = wedge.r * 0.6 * np.cos(np.deg2rad(angle))  # Позиция по оси X
                        y = wedge.r * 0.6 * np.sin(np.deg2rad(angle))  # Позиция по оси Y
                        plt.text(x, y, f'{count} ({percentage:.1f}%)', ha='center', va='center')

            # Сохраняем диаграмму в файл
            chart_filename = "test_statistics_pie_chart.png"
            plt.savefig(chart_filename)
            plt.close()  # Закрываем фигуру, чтобы не занимать память

            return chart_filename

        def show_test_statistics(message, test_id):
            statistics = DB_statistic.get_test_statistics_pie(test_id)  # Получаем статистику
            if statistics:
                started_count = statistics['started']
                completed_count = statistics['completed']
                test_title = DB_get.get_test_title_by_id(test_id)  # Получаем название теста

                # Создаем круговую диаграмму
                chart_filename = create_test_statistics_pie_chart(started_count, completed_count, test_title)

                # Отправляем изображение пользователю
                with open(chart_filename, 'rb') as chart_file:
                    self.bot.send_photo(message.chat.id, chart_file)
            else:
                markup = types.InlineKeyboardMarkup()
                button = types.InlineKeyboardButton("<< Назад к меню теста", callback_data=f'test_{test_id}')
                markup.add(button)
                self.bot.send_message(message.chat.id, "Нет доступной статистики для этого теста.", reply_markup=markup)

            send_button(message, test_id)

        def send_button(message, test_id):
            markup = types.InlineKeyboardMarkup()
            button = types.InlineKeyboardButton("<< Назад к меню теста", callback_data=f'test_{test_id}')
            markup.add(button)
            self.bot.send_message(message.chat.id, "Вернуться к тесту:", reply_markup=markup)

        @self.bot.message_handler(commands=['my_tests'])
        def handle_my_tests(message):
            user_id = message.chat.id  # Получаем ID пользователя
            tests = DB_get.get_user_tests(user_id)  # Получаем список тестов

            if tests:
                markup = types.InlineKeyboardMarkup()
                for test_id, title in tests:
                    # Создаем кнопку для каждого теста
                    button = types.InlineKeyboardButton(title, callback_data=f'test_{test_id}')
                    markup.add(button)

                button_c = types.InlineKeyboardButton("СОЗДАТЬ НОВЫЙ ТЕСТ", callback_data='create_test')
                markup.add(button_c)
                self.bot.send_message(message.chat.id, "Ваши тесты:", reply_markup=markup)

            else:
                markup = types.InlineKeyboardMarkup()
                button = types.InlineKeyboardButton("СОЗДАТЬ НОВЫЙ ТЕСТ", callback_data='create_test')
                markup.add(button)
                self.bot.send_message(message.chat.id, "У вас нет созданных тестов.", reply_markup=markup)

        def about_test(message, test_id):
            test_info, question_count = DB_get.get_test_info(test_id)  # Получаем информацию о тесте

            if test_info:
                title, time_per_question, description, link = test_info
                message_text = (
                    f"Название: {title}\n"
                    f"Описание: {description}\n"
                    f"Количество вопросов: {question_count}\n"
                    f"Время на каждый вопрос: {time_per_question} секунд\n"
                    f"Ссылка на тест: {link}"
                )

                # Создаем кнопки для дальнейших действий
                markup = types.InlineKeyboardMarkup()
                edit_button = types.InlineKeyboardButton("Редактировать", callback_data=f'edit_test_{test_id}')
                statistics_button = types.InlineKeyboardButton("Статистика", callback_data=f'statistics_{test_id}')
                excel_button = types.InlineKeyboardButton("Статистика в Excel",
                                                          callback_data=f'statisticsexcel_{test_id}')
                back_button = types.InlineKeyboardButton("<< Назад к тестам", callback_data=f'my_tests')
                start_test_button = types.InlineKeyboardButton("Пройти тест >>", callback_data=f'goTest_{test_id}')
                delete_button = types.InlineKeyboardButton("Удалить тест", callback_data=f"deleteTest_{test_id}")

                markup.add(edit_button, statistics_button, excel_button)
                markup.add(back_button, start_test_button)
                markup.add(delete_button)
                self.bot.send_message(message.chat.id, message_text, reply_markup=markup)

            else:
                self.bot.send_message(message.chat.id, "Не удалось получить информацию о тесте.")

        def export_test_statistics_to_excel(test_id):
            """Экспортирует статистику теста в Excel файл по заданному test_id."""
            # Список для хранения данных
            data = []

            # Получаем название теста
            title = DB_get.get_test_title_by_id(test_id)

            # Получаем статистику по тесту
            started_count = DB_get.get_started_count(test_id)  # Количество начавших тест
            completed_count = DB_get.get_completed_count(test_id)  # Количество завершивших тест

            # Получаем вопросы и их статистику
            questions = DB_get.get_questions_by_test_id(test_id)  # Получаем вопросы по ID теста

            # Добавляем информацию о тесте в первую строку
            data.append({
                'Название теста': title,
                'Число, смотревших тест': started_count,
                'Число, завершивших тест': completed_count,
                'Вопрос': '',
                'Число, ответивших на вопрос': '',
                'Число, верно ответивших': ''
            })

            for question in questions:
                question_id = question[0]  # Используем числовой индекс для доступа к question_id
                question_text = question[2]  # Используем числовой индекс для доступа к тексту вопроса
                answered_count = DB_get.get_answered_count(question_id)  # Количество ответивших на вопрос
                correct_count = DB_get.get_correct_answered_count(question_id)  # Количество ответивших верно

                # Добавляем данные о вопросе в список
                data.append({
                    'Название теста': '',  # Оставляем пустым, чтобы не дублировать название
                    'Число, смотревших тест': '',
                    'Число, завершивших тест': '',
                    'Вопрос': question_text,
                    'Число, ответивших на вопрос': answered_count,
                    'Число, верно ответивших': correct_count,
                })

            # Создаем DataFrame из списка данных
            df = pd.DataFrame(data)

            test_title = DB_get.get_test_title_by_id(test_id)
            # Сохраняем DataFrame в Excel файл
            excel_filename = f"test_statistics_{test_title}.xlsx"  # Уникальное имя файла для каждого теста

            with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)

                # Получаем доступ к рабочему листу для изменения ширины колонок
                worksheet = writer.sheets['Sheet1']

                for column in worksheet.columns:
                    max_length = 0
                    column_letter = get_column_letter(column[0].column)  # Получаем букву колонки

                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass

                    adjusted_width = (max_length + 2)  # Устанавливаем ширину колонки с небольшим запасом
                    worksheet.column_dimensions[column_letter].width = adjusted_width

            return excel_filename  # Возвращаем имя файла для дальнейшего использования

        def send_excel(message, test_id):
            # Экспортируем статистику в Excel
            excel_file = export_test_statistics_to_excel(test_id)

            markup = types.InlineKeyboardMarkup()
            back_button = types.InlineKeyboardButton("<< Назад к меню теста", callback_data=f'de')
            markup.add(back_button)

            # Отправляем файл пользователю
            with open(excel_file, 'rb') as file:
                self.bot.send_document(message.chat.id, file, reply_markup=markup)

        def edit_menu(message, test_id):
            test_info, question_count = DB_get.get_test_info(test_id)  # Получаем информацию о тесте

            if test_info:
                title, time_per_question, description, link = test_info
                message_text = (
                    f"Название: {title}\n"
                    f"Описание: {description}\n"
                    f"Количество вопросов: {question_count}\n"
                    f"Время на каждый вопрос: {time_per_question} секунд\n"
                    f"Ссылка: {link}"
                )

                markup = types.InlineKeyboardMarkup()

                # Создаем кнопки для редактирования
                edit_title_button = types.InlineKeyboardButton("Изменить название",
                                                               callback_data=f'editTitle_{test_id}')
                edit_description_button = types.InlineKeyboardButton("Изменить описание",
                                                                     callback_data=f'editDescription_{test_id}')
                edit_timer_button = types.InlineKeyboardButton("Изменить таймер", callback_data=f'editTimer_{test_id}')
                edit_question_button = types.InlineKeyboardButton("Изменить вопросы",
                                                                  callback_data=f'editQuestion_{test_id}')
                button = types.InlineKeyboardButton("<< Назад к меню теста", callback_data=f'test_{test_id}')

                # Добавляем кнопки в разметку
                markup.add(edit_title_button)
                markup.add(edit_description_button)
                markup.add(edit_timer_button)
                markup.add(edit_question_button)
                markup.add(button)

                # Отправляем сообщение с кнопками
                self.bot.send_message(message.chat.id, message_text, reply_markup=markup)
            else:
                self.bot.send_message(message.chat.id, "Не удалось получить информацию о тесте.")

        def edit_title(message, test_id):
            self.bot.send_message(message.chat.id, "Введите новое название теста:")
            self.bot.register_next_step_handler(message, save_new_title, test_id)

        def save_new_title(message, test_id):
            markup = types.InlineKeyboardMarkup()
            button = types.InlineKeyboardButton("<< Назад к меню изменений", callback_data=f'edit_test_{test_id}')
            markup.add(button)

            new_title = message.text
            # Обновляем название теста в базе данных
            DB_update.update_test_title(test_id, new_title)

            self.bot.send_message(message.chat.id, f"Название теста обновлено на: '{new_title}'", reply_markup=markup)

        def edit_description(message, test_id):
            self.bot.send_message(message.chat.id, "Введите новое описание теста:")
            self.bot.register_next_step_handler(message, save_new_description, test_id)

        def save_new_description(message, test_id):
            markup = types.InlineKeyboardMarkup()
            button = types.InlineKeyboardButton("<< Назад к меню изменений", callback_data=f'edit_test_{test_id}')
            markup.add(button)

            new_description = message.text

            DB_update.update_test_description(test_id, new_description)
            self.bot.send_message(message.chat.id, f"Описание теста обновлено на: '{new_description}'", reply_markup=markup)

        def edit_timer(message, test_id):
            markup = types.InlineKeyboardMarkup()
            ten_button = types.InlineKeyboardButton("10с", callback_data=f"time_10_{test_id}")
            three_button = types.InlineKeyboardButton("30с", callback_data=f'time_30_{test_id}')
            min_button = types.InlineKeyboardButton("1м", callback_data=f'time_60_{test_id}')
            markup.row(ten_button, three_button, min_button)
            self.bot.send_message(message.chat.id,
                             'Сколько времени будет отводиться на один вопрос: 10 секунд, 30 или 1 минута?',
                             reply_markup=markup)

        def save_new_time(message, timer, test_id):
            markup = types.InlineKeyboardMarkup()
            button = types.InlineKeyboardButton("<< Назад к меню изменений", callback_data=f'edit_test_{test_id}')
            markup.add(button)

            DB_update.update_test_time(test_id, timer)
            self.bot.send_message(message.chat.id, f"Время на прохождение теста обновлено на: {timer} секунд.",
                             reply_markup=markup)

        def edit_question(message, test_id):
            markup = types.InlineKeyboardMarkup()
            add_ques = types.InlineKeyboardButton("Добавить вопрос", callback_data=f"addQuestion_{test_id}")
            del_ques = types.InlineKeyboardButton("Удалить вопрос", callback_data=f"delQuestion_{test_id}")
            button = types.InlineKeyboardButton("<< Назад к меню изменений", callback_data=f'edit_test_{test_id}')
            markup.add(add_ques, del_ques)
            markup.add(button)

            info = DB_get.get_test_info(test_id)
            test_title = info[0][0]  # Имя теста
            question_count = info[1]  # Количество вопросов

            self.bot.send_message(message.chat.id, f'Тест: {test_title}\nвопросы: {question_count}', reply_markup=markup)

        def choose_question_to_delete(message, test_id):
            """Получает список вопросов для теста и отправляет их в виде кнопок."""
            # Получаем список вопросов из базы данных
            questions = DB_get.get_questions_by_test_id(test_id)  # Предполагается, что у вас есть такая функция в db

            if not questions:
                self.bot.send_message(message.chat.id, "В этом тесте нет вопросов.")
                return

            markup = types.InlineKeyboardMarkup()

            for question in questions:
                question_id = question[0]  # Предполагается, что question_id - это первый элемент кортежа
                question_text = question[2]  # Предполагается, что текст вопроса - это третий элемент
                button = types.InlineKeyboardButton(question_text, callback_data=f'question_{question_id}_{test_id}')
                markup.add(button)

            back = types.InlineKeyboardButton("<< Назад к меню вопросов", callback_data=f'editQuestion_{test_id}')
            markup.add(back)

            self.bot.send_message(message.chat.id, "Выберите вопрос, который хотите удалить:", reply_markup=markup)

        def delete_question(message, question_id, test_id):
            markup = types.InlineKeyboardMarkup()
            back = types.InlineKeyboardButton("<< Назад к списку вопросов", callback_data=f'delQuestion_{test_id}')
            markup.add(back)

            DB_delete.delete_question(question_id)
            self.bot.send_message(message.chat.id, "Вопрос удалён.", reply_markup=markup)

        def delete_test(message, test_id):
            markup = types.InlineKeyboardMarkup()
            back = types.InlineKeyboardButton("<< Назад к тестам", callback_data=f'my_tests')
            markup.add(back)

            DB_delete.delete_test(test_id)
            self.bot.send_message(message.chat.id, "Тест удалён.", reply_markup=markup)

        @self.bot.message_handler(commands=['about'])
        def handle_about_bot(message):
            commands = [
                ("/start", "старт"),
                ("/create_test", "создать тест"),
                ("/my_tests", "ваши тесты"),
                ("/about", "о боте"),
                ("/txt_test", "отправить тест в формате txt файла")
            ]

            command_text = ("Здесь ты можешь создавать свои собственные тесты."
                            "\n\nТы можешь управлять ботом с помощью доступных команд:\n\n")
            for command, description in commands:
                command_text += f"{command} - {description}\n"

            self.bot.send_message(message.chat.id, command_text.strip())  # Убираем лишний перевод строки в конце
