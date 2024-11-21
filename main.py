import telebot
from telebot import types
import dataBase as db

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

    def start(self):
        @bot.message_handler(commands=['start'])
        def handle_start(message):
            markup = types.InlineKeyboardMarkup()
            btn1 = types.InlineKeyboardButton("Создать тест", callback_data='create_test')
            btn2 = types.InlineKeyboardButton("Мои тесты", callback_data='my_tests')
            btn3 = types.InlineKeyboardButton("О боте", callback_data='about_bot')
            markup.row(btn1, btn2)
            markup.row(btn3)
            bot.send_message(message.chat.id, 'Добро пожаловать!', reply_markup=markup)

        @bot.callback_query_handler(func=lambda call: True)
        def on_click(call):
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
            elif call.data == "vvod":
                save_type_question(call.message, "вариант")
            elif call.data == "variant":
                save_type_question(call.message, "ввод")
            elif call.data == 'add_answer':
                make_answer(call.message)
            elif call.data == 'make_question':
                save_question(call.message)
            elif call.data == 'done':
                done_test(call.message)

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

            type_question(message)


        def save_description(message):
            bot.send_message(message.chat.id, "Введите описание:")
            bot.register_next_step_handler(message,save_description_in_db)


        def save_description_in_db(message):
            description = message.text
            self.current_test_id = db.save_test(message.from_user.id, self.current_test_title, description)
            bot.send_message(message.chat.id, f"Тест '{self.current_test_title}' с описанием '{description}' создан!")
            type_question(message)

        def type_question(message):
            markup = types.InlineKeyboardMarkup()
            variant_button = types.InlineKeyboardButton("С выбором варианта/вариантов", callback_data='variant')
            vvod_button = types.InlineKeyboardButton("Ввод ответа", callback_data='vvod')
            markup.add(variant_button)
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
            answer_text = message.text

            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add('Да', 'Нет')
            bot.send_message(message.chat.id, "Это правильный ответ?", reply_markup=markup)

            bot.register_next_step_handler(message, lambda m: save_answer_in_db(m, answer_text))

        def save_answer_in_db(message, answer_text):
            is_correct = True if message.text.lower() == 'да' else False
            db.save_answer(self.current_question_id, answer_text, is_correct)

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

        def done_test(message):
            bot.send_message(message.chat.id, "Тест сохранён")











        @bot.message_handler(commands=['my_tests'])
        def handle_my_tests(message):
            bot.send_message(message.chat.id, "Ваши тесты...")

        @bot.message_handler(commands=['about_bot'])
        def handle_about_bot(message):
            bot.send_message(message.chat.id, "О боте...")




test_bot_instance = TestBot()
test_bot_instance.start()


bot.polling(none_stop=True)