import telebot
from telebot import types
import dataBase as db
import matplotlib
matplotlib.use('Agg')  # Используем бэкенд Agg
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from openpyxl import Workbook
from openpyxl.utils import get_column_letter

TOKEN = '7952186657:AAFOWLSyUhqdrBFYE4TNajUfXPG3W4g-ETs'
bot = telebot.TeleBot(TOKEN)
db.create_tables()

class TestBot:
    def __init__(self):
        self.current_test_title = None
        self.current_test_id = None
        self.current_question_id = None
        self.current_question = None
        self.current_type = None
        self.link = None
        self.user_answers = []
        self.correct_answers_from_user = 0
        self.current_question_index = 0
        self.time = 10
        self.questions = []
        self.timer = None
        self.question_type = None
        self.correct = None
        self.question_data = None

    def start(self):

        @bot.message_handler(commands=['start'])
        def handle_start(message):
            if ' ' in message.text:
                s = message.text.split(' ')
                test_id = s[-1]
                # test_id = int(message.text[-1])
                start_test(message, test_id)

            else:
                markup = types.InlineKeyboardMarkup()
                btn1 = types.InlineKeyboardButton("Создать тест", callback_data='create_test')
                btn2 = types.InlineKeyboardButton("Мои тесты", callback_data='my_tests')
                btn3 = types.InlineKeyboardButton("О боте", callback_data='about_bot')
                markup.row(btn1, btn2)
                markup.row(btn3)
                bot.send_message(message.chat.id, 'Добро пожаловать!', reply_markup=markup)
            print(f"Received command: {message.text}")


        @bot.callback_query_handler(func=lambda call: True)
        def on_click(call):
            # Обработка нажатий на кнопки с test_id
            if call.data.startswith('test_'):
                test_id = int(call.data.split('_')[1])  # Извлекаем test_id из callback_data
                about_test(call.message, test_id)  # Запускаем выбранный тест
            elif call.data.startswith('edit_test_'):
                test_id = int(call.data.split('_')[2])
            elif call.data.startswith('statistics_'):
                test_id = int(call.data.split('_')[1])
                view_statistics(call.message, test_id)
            elif call.data.startswith('statisticsexcel_'):
                test_id = int(call.data.split('_')[1])
                send_excel(call.message, test_id)
            else:
                if call.data == "create_test":
                    handle_test(call.message)
                elif call.data == "my_tests":
                    handle_my_tests(call.message)
                elif call.data == "about_bot":
                    handle_about_bot(call.message)
                elif call.data == 'skip_description':
                    skip_description(call.message)
                elif call.data == "input_disc":
                    save_description(call.message)
                elif call.data == "10":
                    self.time= 10
                    save_time(call.message)
                elif call.data == "30":
                    self.time = 30
                    save_time(call.message)
                elif call.data == "1":
                    self.time = 60
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
                elif call.data == 'share_test':
                    pass
                elif call.data == 'add_to_group':
                    pass
                elif call.data == 'take_test':
                    start_test(call.message, self.current_test_id)




        @bot.message_handler(commands=['test'])
        def handle_test(message):
            db.add_user(message.from_user.id)
            bot.send_message(message.chat.id, "Введите название теста.")
            bot.register_next_step_handler(message, save_test_title)


        def save_test_title(message):
            self.current_test_title = message.text

            markup = types.InlineKeyboardMarkup()
            skip_button = types.InlineKeyboardButton("Пропустить", callback_data='skip_description')
            input_button = types.InlineKeyboardButton("Ввести описание", callback_data='input_disc')
            markup.add(skip_button, input_button)
            bot.send_message(message.chat.id, 'Вы можете добавить описание к тесту, а можете пропустить этот шаг', reply_markup=markup)


        def skip_description(message):
            user_id = message.from_user.id
            self.current_test_id = db.save_test(user_id, self.current_test_title, None)

            bot.send_message(message.chat.id, f"Тест '{self.current_test_title}' создан без описания.")
            save_link(message)


        def save_description(message):
            bot.send_message(message.chat.id, "Введите описание:")
            bot.register_next_step_handler(message,save_description_in_db)


        def save_description_in_db(message):
            description = message.text
            self.current_test_id = db.save_test(message.from_user.id, self.current_test_title, description)
            bot.send_message(message.chat.id, f"Тест '{self.current_test_title}' с описанием '{description}' создан!")
            save_link(message)

        def save_link(message):
            t_id = self.current_test_id
            self.link = f"https://t.me/TheCreatorOfTheTestsBot?start={t_id}"
            db.save_link(self.link, self.current_test_id)
            time(message)

        def time(message):
            markup = types.InlineKeyboardMarkup()
            ten_button = types.InlineKeyboardButton("10с", callback_data="10")
            three_button = types.InlineKeyboardButton("30с", callback_data='30')
            min_button = types.InlineKeyboardButton("1м", callback_data='1')
            markup.row(ten_button, three_button, min_button)
            bot.send_message(message.chat.id,
                             'Сколько времени будет отводиться на один вопрос: 10 секунд, 30 или 1 минута?',
                             reply_markup=markup)


        def save_time(message):
            t_id = self.current_test_id
            db.save_test_time(t_id, self.time)
            type_question(message)


        def type_question(message):
            markup = types.InlineKeyboardMarkup()
            one_button = types.InlineKeyboardButton("один правильный ответ", callback_data="one")
            several_button = types.InlineKeyboardButton("несколько правильных ответов", callback_data='several')
            vvod_button = types.InlineKeyboardButton("ввод с клавиатуры", callback_data='vvod')
            markup.add(one_button)
            markup.add(several_button)
            markup.add(vvod_button)
            bot.send_message(message.chat.id, 'Вы можете создать вопрос с вариантами ответа, а можете сделать ввод ответа пользователем',
            reply_markup=markup)

        def save_type_question(message, tip):
            self.current_type = tip
            save_question(message)


        def save_question(message):
            bot.send_message(message.chat.id, 'Введите вопрос.')
            bot.register_next_step_handler(message, save_question_in_db)

        def save_question_in_db(message):
            self.current_question = message.text
            self.current_question_id = db.save_question(self.current_test_id, self.current_question, self.current_type)

            bot.send_message(message.chat.id, "Вопрос сохранен.")
            make_answer(message)

        def make_answer(message):
            bot.send_message(message.chat.id, "Введите вариант ответа:")
            bot.register_next_step_handler(message, save_answer)


        def save_answer(message):
            if self.current_type == "vvod":
                save_answer_in_db(message, message.text)
            else:
                answer_text = message.text

                markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
                markup.add('Да', 'Нет')
                bot.send_message(message.chat.id, "Это правильный ответ?", reply_markup=markup)

                bot.register_next_step_handler(message, lambda m: save_answer_in_db(m, answer_text))

        def save_answer_in_db(message, answer_text = "да"):
            if message.text.lower() == 'да' or self.current_type == "vvod":
                is_correct = True
            else:
                is_correct = False
            #bot.send_message(message.chat.id, str(is_correct))
            db.save_answer(self.current_question_id, answer_text, is_correct)

            count = db.count_answers_by_question_id(self.current_question_id)

            if self.current_type != "vvod" and count < 2:
                markup = types.InlineKeyboardMarkup()
                button1 = types.InlineKeyboardButton("Добавить вариант ответа", callback_data='add_answer')
                markup.row(button1)
                bot.send_message(message.chat.id, "Вариант ответа сохранен. Добавьте ещё вариант ответа для теста",
                                 reply_markup=markup)
            elif self.current_type != "vvod":
                markup = types.InlineKeyboardMarkup()
                button1 = types.InlineKeyboardButton("Добавить вариант ответа", callback_data='add_answer')
                button2 = types.InlineKeyboardButton("Создать вопрос", callback_data='make_question')
                button3 = types.InlineKeyboardButton("Закончить создание теста", callback_data='done')
                markup.row(button1)
                markup.row(button2)
                markup.row(button3)
                bot.send_message(message.chat.id,
                "Вариант ответа сохранен. Вы можете добавить еще один вариант ответа или создать ещё вопрос или закончить создание теста.",
                reply_markup=markup)
            elif self.current_type == "vvod":
                markup = types.InlineKeyboardMarkup()
                button2 = types.InlineKeyboardButton("Создать вопрос", callback_data='make_question')
                button3 = types.InlineKeyboardButton("Закончить создание теста", callback_data='done')
                markup.row(button2)
                markup.row(button3)
                bot.send_message(message.chat.id,
                                 "Вариант ответа сохранен. Вы можете создать ещё вопрос или закончить создание теста.",
                                 reply_markup=markup)


        def done_test(message):
            markup = types.InlineKeyboardMarkup()
            share_button = types.InlineKeyboardButton("Поделиться", callback_data='share_test')
            markup.add(share_button)
            add_to_group_button = types.InlineKeyboardButton("Добавить в группу", callback_data='add_to_group')
            markup.add(add_to_group_button)
            take_test_button = types.InlineKeyboardButton("Пройти тест", callback_data='take_test')
            markup.add(take_test_button)

            t_id = self.current_test_id
            bot.send_message(
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
            self.time = db.get_test_time(test_id)
            if db.test_exists(test_id):
                bot.send_message(message.chat.id, f"Вы начали тест с ID: {test_id}.")
                db.increment_started_count(test_id)
                self.questions = db.get_questions_by_test_id(test_id)
                send_question(message, test_id)
            else:
                bot.send_message(message.chat.id, "Такого теста не существует")

        def send_question(message, test_id):
            length = len(self.questions)

            if self.current_question_index < length:
                self.question_data = self.questions[self.current_question_index]
                question_text = self.question_data[2]
                self.question_type = self.question_data[3]


                if self.question_type == "one":
                    options = db.get_answers_by_question_id(self.question_data[0])
                    self.option_texts = [option[2] for option in options]

                    #id_s = db.get_question_ids_by_test_id(test_id)
                    self.correct = db.get_correct_answer_by_question_id(self.question_data[0])

                    if self.correct in self.option_texts:
                        correct_id = self.option_texts.index(self.correct)

                    self.current_question_index += 1

                    bot.send_poll(message.chat.id, question_text, self.option_texts, allows_multiple_answers=False,
                                  type='quiz', correct_option_id=correct_id, open_period=self.time, is_anonymous=False)


                elif self.question_type == "several":
                    options = db.get_answers_by_question_id(self.question_data[0])
                    self.option_texts = [option[2] for option in options]

                    #id_s = db.get_question_ids_by_test_id(test_id)
                    self.correct = db.get_correct_answers_by_question_id(self.question_data[0])

                    self.current_question_index += 1

                    bot.send_poll(message.chat.id, question_text, self.option_texts, allows_multiple_answers=True,
                                  type="regular", open_period=self.time, is_anonymous=False)


                elif self.question_type == "vvod":
                    bot.send_message(message.chat.id, question_text)
                    bot.register_next_step_handler_by_chat_id(message.chat.id, handle_text_answer, test_id)



                @bot.poll_answer_handler()
                def handle_poll_answer(poll_answer):
                    if self.question_type == "several":
                        correct_indices = get_correct_answer_indices(self.option_texts, self.correct)

                        # Преобразуем списки в множества для удобства сравнения
                        user_answers_set = set(poll_answer.option_ids)
                        correct_answers_set = set(correct_indices)

                        if user_answers_set == correct_answers_set:
                            db.update_question_statistics(self.question_data[0], test_id, True)
                            self.correct_answers_from_user += 1
                            bot.send_message(message.chat.id, "Все ответы правильные!")
                        else:
                            db.update_question_statistics(self.question_data[0], test_id, False)
                            bot.send_message(message.chat.id,
                                             f"Неверно. Правильные ответы: {', '.join(self.correct)}")



                        send_question(message, test_id)

                    elif self.question_type == "one":
                        if self.option_texts[poll_answer.option_ids[0]] == self.correct:
                            db.update_question_statistics(self.question_data[0], test_id, True)
                            self.correct_answers_from_user += 1
                        else:
                            db.update_question_statistics(self.question_data[0], test_id, False)

                        send_question(message, test_id)

            else:
                db.increment_completed_count(test_id)
                statistic_for_user(message, length, test_id)



        def handle_text_answer(message, test_id):

            #id_s = db.get_question_ids_by_test_id(test_id)
            self.correct = db.get_correct_answer_by_question_id(self.question_data[0])
            if message.text.lower() == self.correct:
                db.update_question_statistics(self.question_data[0], test_id, True)
                bot.send_message(message.chat.id, "Правильный ответ")
                self.correct_answers_from_user += 1
            else:
                db.update_question_statistics(self.question_data[0], test_id, False)
                bot.send_message(message.chat.id, f"Неверно. Правильный ответ: {self.correct}")



            self.current_question_index += 1
            send_question(message, test_id)

        def statistic_for_user(message, total, test_id):
            percent = round((self.correct_answers_from_user / total) * 100, 2)
            bot.send_message(message.chat.id, f"Вы ответили на {self.correct_answers_from_user} из {total}.\n"
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
            #plt.xlabel('Вопросы')
            plt.ylabel('Процент успешности (%)')
            plt.title(f"Статистика успешности по тесту: {test_title}")
            plt.xticks(rotation=45)  # Поворачиваем метки по оси X для лучшей читаемости
            plt.ylim(0, 100)  # Устанавливаем пределы по оси Y от 0 до 100

            # Добавляем проценты на столбиках
            for bar in bars:
                yval = bar.get_height()  # Высота столбика
                plt.text(bar.get_x() + bar.get_width() / 2, yval, f'{yval:.1f}%', ha='center',
                         va='bottom')  # Добавляем текст

            # Сохраняем гистограмму в файл
            chart_filename = "test_statistics_histogram.png"
            plt.tight_layout()  # Автоматически подгоняем размеры графика
            plt.savefig(chart_filename)
            plt.close()  # Закрываем фигуру, чтобы не занимать память

            return chart_filename

        #@bot.message_handler(commands=['view_statistics'])
        def view_statistics(message, test_id):
            statistics = db.get_test_statistics(test_id)

            if not statistics:
                bot.send_message(message.chat.id, "Нет доступной статистики для этого теста.")
                return

            test_title = db.get_test_title_by_id(test_id)

            # Создаем круговую диаграмму
            chart_filename = create_histogram(statistics, test_title)

            # Отправляем изображение пользователю
            with open(chart_filename, 'rb') as chart_file:
                bot.send_photo(message.chat.id, chart_file)

            show_test_statistics(message, test_id)


        def create_test_statistics_pie_chart(started_count, completed_count, test_title):
            """Создает круговую диаграмму статистики по тесту."""
            labels = ['Завершили тест', 'Не завершили тест']
            sizes = [completed_count, started_count - completed_count]

            colors = ['orange', 'grey']  # Зеленый для завершивших и красный для не завершивших
            plt.figure(figsize=(8, 8))
            wedges, texts, autotexts = plt.pie(sizes, labels=labels, colors=colors, autopct='', startangle=140)
            plt.axis('equal')  # Равные оси для круга
            plt.title(f"Статистика по тесту: {test_title}")

            # Добавляем текст с количеством и процентом на диаграмму
            for i, wedge in enumerate(wedges):
                angle = (wedge.theta2 + wedge.theta1) / 2.0  # Находим угол для размещения текста
                x = wedge.r * 0.6 * np.cos(np.deg2rad(angle))  # Позиция по оси X
                y = wedge.r * 0.6 * np.sin(np.deg2rad(angle))  # Позиция по оси Y
                count = sizes[i]
                percentage = count / started_count * 100
                plt.text(x, y, f'{count} ({percentage:.1f}%)', ha='center', va='center')

            # Сохраняем диаграмму в файл
            chart_filename = "test_statistics_pie_chart.png"
            plt.savefig(chart_filename)
            plt.close()  # Закрываем фигуру, чтобы не занимать память

            return chart_filename

        def show_test_statistics(message, test_id):
            statistics = db.get_test_statistics_pie(test_id)  # Получаем статистику
            if statistics:
                started_count = statistics['started']
                completed_count = statistics['completed']
                test_title = db.get_test_title_by_id(test_id)  # Получаем название теста

                # Создаем круговую диаграмму
                chart_filename = create_test_statistics_pie_chart(started_count, completed_count, test_title)

                # Отправляем изображение пользователю
                with open(chart_filename, 'rb') as chart_file:
                    bot.send_photo(message.chat.id, chart_file)
            else:
                bot.send_message(message.chat.id, "Нет доступной статистики для этого теста.")
            send_button(message, test_id)

        def send_button(message, test_id):
            markup = types.InlineKeyboardMarkup()
            button = types.InlineKeyboardButton("<<к меню теста", callback_data=f'test_{test_id}')
            markup.add(button)
            bot.send_message(message.chat.id, "Вернуться к тесту:", reply_markup=markup)

        @bot.message_handler(commands=['my_tests'])
        def handle_my_tests(message):
            user_id = message.from_user.id  # Получаем ID пользователя
            tests = db.get_user_tests(user_id)  # Получаем список тестов

            if tests:
                markup = types.InlineKeyboardMarkup()
                for test_id, title in tests:
                    # Создаем кнопку для каждого теста
                    button = types.InlineKeyboardButton(title, callback_data=f'test_{test_id}')
                    markup.add(button)

                button = types.InlineKeyboardButton("СОЗДАТЬ НОВЫЙ ТЕСТ", callback_data='create_test')
                markup.add(button)

                bot.send_message(message.chat.id, "Ваши тесты:", reply_markup=markup)
            else:
                markup = types.InlineKeyboardMarkup()
                button = types.InlineKeyboardButton("СОЗДАТЬ НОВЫЙ ТЕСТ", callback_data='create_test')
                markup.add(button)
                bot.send_message(message.chat.id, "У вас нет созданных тестов.", reply_markup=markup)

        def about_test(message, test_id):
            test_info, question_count = db.get_test_info(test_id)  # Получаем информацию о тесте

            if test_info:
                title, time_per_question = test_info
                message_text = (
                    f"Название теста: {title}\n"
                    f"Количество вопросов: {question_count}\n"
                    f"Время на каждый вопрос: {time_per_question} секунд"
                )

                # Создаем кнопки для дальнейших действий
                markup = types.InlineKeyboardMarkup()
                edit_button = types.InlineKeyboardButton("Редактировать", callback_data=f'edit_test_{test_id}')
                statistics_button = types.InlineKeyboardButton("Статистика", callback_data=f'statistics_{test_id}')
                excel_button = types.InlineKeyboardButton("Статистика в Excel", callback_data=f'statisticsexcel_{test_id}')

                markup.add(edit_button, statistics_button, excel_button)
                bot.send_message(message.chat.id, message_text, reply_markup=markup)

            else:
                bot.send_message(message.chat.id, "Не удалось получить информацию о тесте.")

        def export_test_statistics_to_excel(test_id):
            """Экспортирует статистику теста в Excel файл по заданному test_id."""
            # Список для хранения данных
            data = []

            # Получаем название теста
            title = db.get_test_title_by_id(test_id)

            # Получаем статистику по тесту
            started_count = db.get_started_count(test_id)  # Количество начавших тест
            completed_count = db.get_completed_count(test_id)  # Количество завершивших тест

            # Получаем вопросы и их статистику
            questions = db.get_questions_by_test_id(test_id)  # Получаем вопросы по ID теста

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
                answered_count = db.get_answered_count(question_id)  # Количество ответивших на вопрос
                correct_count = db.get_correct_answered_count(question_id)  # Количество ответивших верно

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

            # Сохраняем DataFrame в Excel файл
            excel_filename = f"test_statistics_{test_id}.xlsx"  # Уникальное имя файла для каждого теста

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

            # Отправляем файл пользователю
            with open(excel_file, 'rb') as file:
                bot.send_document(message.chat.id, file)


        @bot.message_handler(commands=['about_bot'])
        def handle_about_bot(message):
            bot.send_message(message.chat.id, "О боте... {в разработке}")




test_bot_instance = TestBot()
test_bot_instance.start()


bot.polling(none_stop=True)